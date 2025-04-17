from itertools import product

from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, BasketItems, Payment, Tag, Review
from django.conf import settings
from django.utils.timezone import now

from .models import Category, Subcategory, Basket, Order, DeliveryCost, SaleItem
from userauth.models import Profile
from .serializers import BannerListSerializer, CatalogListSerializer, ProductSerializer, BasketItemSerializer, \
    OrderSerializers, TagSerializer, SaleItemSerializer, ReviewSerializer
from django.contrib.auth.models import User


class CategoryView(GenericAPIView):
    def get(self, request):
        category = Category.objects.all()
        category_data = []
        for category_i in category:
            subcategory = category_i.subcategory_set.all()
            subcategory_data = []

            for subcategory_i in subcategory:
                data_sub = {
                    'id': subcategory_i.pk,
                    'title': subcategory_i.title,
                    'image': subcategory_i.get_image(),
                }
                subcategory_data.append(data_sub)
            data_cat = {
                'id': category_i.pk,
                'title': category_i.title,
                'image': category_i.get_image(),
                'subcategories': subcategory_data
            }
            category_data.append(data_cat)

        return JsonResponse(category_data, safe=False)


class ProductListView(APIView):
    def filter_queryset(self, products):
        category_id = self.request.GET.get('category')
        min_price = float(self.request.GET.get('filter[minPrice]', 0))
        max_price = float(self.request.GET.get('filter[maxPrice]', float('inf')))
        freeDelivery = self.request.GET.get('filter[freeDelivery]', '').lower() == 'true'
        avialable = self.request.GET.get('filter[available]', '').lower() == 'true'
        name = self.request.GET.get('filter[name]', '').strip()
        tags = self.request.GET.getlist('tags[]')
        sort_field = self.request.GET.get('sort', 'id')
        sort_type = self.request.GET.get('sortType', 'inc')

        if category_id:
            products = products.filter(category_id=category_id)
        if freeDelivery:
            products = products.filter(freeDelivery=True)
        if avialable:
            products = products.filter(count__gt=0)
        if name:
            products = products.filter(title__icontains=name)
        for tag in tags:
            products = products.filter(tags__title=tag)
        if sort_type == 'inc':
            products = products.order_by(sort_field)
        else:
            products = products.order_by('-' + sort_field)

        products = products.filter(price__gte=min_price, price__lte=max_price)
        return products

    def get(self, request):
        products = Product.objects.all()
        filtered_products = self.filter_queryset(products)
        page_number = int(request.GET.get('currentPage', 1))
        limit = 2
        paginator = Paginator(filtered_products, limit)
        page = paginator.get_page(page_number)
        product_data = []
        for product in page:
            product_data.append(
                {
                    'id': product.pk,
                    'category': product.category.pk,
                    'price': product.price,
                    'count': product.count,
                    'date': product.date,
                    'title': product.title,
                    'description': product.description,
                    'freeDelivery': product.freeDelivery,
                    'images': product.get_image(),
                    'tags': list(product.tags.values_list('title', flat=True)),
                    'reviews': product.get_rating(),
                    'rating': float(product.rating)
                }
            )

        catalog_data = {
            'items': product_data,
            'currentPage': page_number,
            'lastPage': paginator.num_pages
        }

        return Response(catalog_data)


class BannerListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.filter(rating__gt=0).order_by('-rating')[:3]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PopularListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.filter(count__gt=0)[:1]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LimitedListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.filter(count__gt=0)[:4]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailApiView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class BasketApiView(APIView):
    def get(self, request):
        queryset = BasketItems.objects.filter(basket__user=request.user)
        serializer = BasketItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        id = request.data['id']
        count = request.data['count']

        if request.user.is_anonymous:
            anon_user, _ = User.objects.get_or_create(username='anonymous')
            basket, _ = Basket.objects.get_or_create(user=anon_user)
        else:
            basket, _ = Basket.objects.get_or_create(user=request.user)

        product = Product.objects.get(id=id)

        basket_item, created = BasketItems.objects.get_or_create(basket=basket, product=product)

        basket_item.quantity = count
        basket_item.save()

        basket_items = BasketItems.objects.filter(basket=basket)
        serializer = BasketItemSerializer(basket_items, many=True)
        return Response(serializer.data)

    def delete(self, request):
        id = request.data['id']
        count = request.data['count']

        try:
            if request.user.is_anonymous:
                anon_user, _ = User.objects.get_or_create(username='anonymous')
                basket, _ = Basket.objects.get_or_create(user=anon_user)
            else:
                basket = request.user.basket

            product = Product.objects.get(id=id)

            basket_item = BasketItems.objects.get(basket=basket, product=product)

            if basket_item.quantity > count:
                basket_item.quantity -= count
                basket_item.save()
            else:
                basket_item.delete()

            basket_items = BasketItems.objects.filter(basket=basket)
            serializer = BasketItemSerializer(basket_items, many=True)

            return Response(serializer.data)

        except Basket.DoesNotExist:
            return Response('Корзина не найдена', status=404)
        except Product.DoesNotExist:
            return Response('Продукт не найден', status=404)
        except BasketItems.DoesNotExist:
            return Response('Товар не найден в корзине', status=404)


class CreateOrderApiView(APIView):
    def post(self, request):
        try:
            basket = request.user.basket
            # profile = User.objects.get(user=request.user)
            basket_items = BasketItems.objects.filter(basket__user=request.user)
            total_cost = 0
            order = Order.objects.create(
                fullName=request.user.username,
                basket=basket
            )
            for item in basket_items:
                product = Product.objects.get(pk=item.product.pk)
                product.count = item.quantity
                total_cost += item.product.price * item.quantity
                product.save()

            delivery_price = DeliveryCost.objects.get(id=1)
            if total_cost > delivery_price.delivery_free_min:
                order.totalCost = total_cost
            else:
                order.totalCost = total_cost + delivery_price.delivery_cost
            order.save()

            response_data = {'orderId': order.pk}
            return JsonResponse(response_data)
        except Basket.DoesNotExist:
            return JsonResponse({'error': 'У данного пользователя ничего в корзине нет'})


class OrderDetailApiView(APIView):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        serializer = OrderSerializers(order)
        return JsonResponse(serializer.data)

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        delivery_type = request.data['deliveryType']
        payment_type = request.data['paymentType']
        city = request.data['city']
        address = request.data['address']
        status_order = 'accepted'

        if delivery_type == 'express':
            delivery_price = DeliveryCost.objects.get(id=1)
            order.totalCost += delivery_price.delivery_express_cost
            order.save()

        order.deliveryType = delivery_type
        order.paymentType = payment_type
        order.city = city
        order.address = address
        order.status = status_order
        order.save()

        response_data = {'orderId': order.pk}
        return Response(response_data, status=200)


class TagApiView(APIView):
    def get(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


class SaleItemListView(APIView):
    def get(self, request):
        current_time = now()
        sale_items = SaleItem.objects.filter(
            dateFrom__lte=current_time,
            dateTo__gte=current_time
        ).order_by('-dateFrom')
        page_number = int(request.GET.get('currentPage', 1))
        limit = 2
        paginator = Paginator(sale_items, limit)
        serializer = SaleItemSerializer(sale_items, many=True)
        data = ({
            'items': serializer.data,
            'currentPage': page_number,
            'lastPage': paginator.num_pages
        })

        return Response(data)


class ReviewCreateAPIView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product=product).order_by('-date')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            author_name = serializer.validated_data['author']

            profile = Profile.objects.filter(fullName=author_name).first()
            if not profile:
                profile = Profile.objects.create(fullName=author_name)

            Review.objects.create(
                author=profile,
                email=serializer.validated_data['email'],
                text=serializer.validated_data['text'],
                rate=serializer.validated_data['rate'],
                product=product
            )

            return Response({'detail': 'Review created'}, status=status.HTTP_201_CREATED)

        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


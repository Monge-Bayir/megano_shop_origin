import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math
import uuid

from .models import (
    Product, BasketItems, Payment, Tag, Review,
    Category, Basket, Order, DeliveryCost
)
from .serializers import (
    BannerListSerializer, ProductSerializer, BasketItemSerializer,
    OrderSerializers, TagSerializer, ReviewSerializer
)
from userauth.models import Profile

##
class CategoryView(GenericAPIView):
    def get(self, request):
        categories = Category.objects.prefetch_related('subcategory_set').all()
        category_data = []
        for category_i in categories:
            subcategory_data = [
                {
                    'id': sub.pk,
                    'title': sub.title,
                    'image': sub.get_image(),
                }
                for sub in category_i.subcategory_set.all()
            ]
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
        request = self.request
        category_id = request.GET.get('category')
        min_price = float(request.GET.get('filter[minPrice]', 0))
        max_price = float(request.GET.get('filter[maxPrice]', float('inf')))
        freeDelivery = request.GET.get('filter[freeDelivery]', '').lower() == 'true'
        avialable = request.GET.get('filter[available]', '').lower() == 'true'
        name = request.GET.get('filter[name]', '').strip()
        tags = request.GET.getlist('tags[]')
        sort_field = request.GET.get('sort', 'id')
        sort_type = request.GET.get('sortType', 'inc')

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
        products = products.filter(price__gte=min_price, price__lte=max_price)
        products = products.order_by(sort_field if sort_type == 'inc' else '-' + sort_field)
        return products

    def get(self, request):
        products = Product.objects.select_related('category').prefetch_related('tags', 'review_set').all()
        filtered_products = self.filter_queryset(products)
        page_number = int(request.GET.get('currentPage', 1))
        limit = 2
        paginator = Paginator(filtered_products, limit)
        page = paginator.get_page(page_number)
        product_data = [{
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
        } for product in page]

        return Response({'items': product_data, 'currentPage': page_number, 'lastPage': paginator.num_pages})


class BannerListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('tags').filter(rating__gt=0).order_by('-rating')[:3]


class PopularListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('tags').filter(count__gt=0)[:1]


class LimitedListApiView(ListAPIView):
    serializer_class = BannerListSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('tags').filter(count__gt=0)[:4]


class ProductDetailApiView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product.objects.select_related('category').prefetch_related('tags', 'review_set'), pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class BasketApiView(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            basket_id = request.session.get('basket_id')
            if not basket_id:
                basket_id = str(uuid.uuid4())  # Генерируем уникальный ID корзины
                request.session['basket_id'] = basket_id
            basket, _ = Basket.objects.get_or_create(session_id=basket_id)
        else:
            basket, _ = Basket.objects.get_or_create(user=request.user)

        queryset = BasketItems.objects.select_related('basket', 'product').filter(basket=basket)
        serializer = BasketItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        id = request.data['id']
        count = request.data['count']

        if request.user.is_anonymous:
            basket_id = request.session.get('basket_id')
            if not basket_id:
                basket_id = str(uuid.uuid4())  # Генерируем уникальный ID корзины
                request.session['basket_id'] = basket_id
            basket, _ = Basket.objects.get_or_create(session_id=basket_id)
        else:
            basket, _ = Basket.objects.get_or_create(user=request.user)

        try:
            product = Product.objects.only('id').get(id=id)
            basket_item, _ = BasketItems.objects.get_or_create(basket=basket, product=product)
            basket_item.quantity = count
            basket_item.save()

            items = BasketItems.objects.select_related('basket', 'product').filter(basket=basket)
            serializer = BasketItemSerializer(items, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response('Продукт не найден', status=404)

    def delete(self, request):
        id = request.data['id']
        count = request.data['count']

        if request.user.is_anonymous:
            basket_id = request.session.get('basket_id')
            if not basket_id:
                basket_id = str(uuid.uuid4())  # Генерируем уникальный ID корзины
                request.session['basket_id'] = basket_id
            basket, _ = Basket.objects.get_or_create(session_id=basket_id)
        else:
            basket, _ = Basket.objects.get_or_create(user=request.user)

        try:
            product = Product.objects.only('id').get(id=id)
            basket_item = BasketItems.objects.get(basket=basket, product=product)

            if basket_item.quantity > count:
                basket_item.quantity -= count
                basket_item.save()
            else:
                basket_item.delete()

            items = BasketItems.objects.select_related('basket', 'product').filter(basket=basket)
            serializer = BasketItemSerializer(items, many=True)
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
            if request.user.is_anonymous:
                basket_id = request.session.get('basket_id')
                if not basket_id:
                    basket_id = str(uuid.uuid4())  # Генерация уникального ID для корзины
                    request.session['basket_id'] = basket_id
                basket = Basket.objects.get(session_id=basket_id)
            else:
                basket = Basket.objects.get(user=request.user)

            basket_items = BasketItems.objects.select_related('product').filter(basket=basket)
            total_cost = 0
            order = Order.objects.create(fullName=request.user.username if not request.user.is_anonymous else 'Guest', basket=basket)

            for item in basket_items:
                product = item.product
                product.count = item.quantity
                total_cost += product.price * item.quantity
                product.save()

            delivery_price = DeliveryCost.objects.only('delivery_cost', 'delivery_free_min').get(id=1)
            order.totalCost = total_cost if total_cost > delivery_price.delivery_free_min else total_cost + delivery_price.delivery_cost
            order.save()

            return JsonResponse({'orderId': order.pk})

        except Basket.DoesNotExist:
            return JsonResponse({'error': 'У данного пользователя ничего в корзине нет'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Один из продуктов не найден'}, status=400)
        except DeliveryCost.DoesNotExist:
            return JsonResponse({'error': 'Не найдена стоимость доставки'}, status=400)



class OrderDetailApiView(APIView):
    def get(self, request, pk):
        order = Order.objects.select_related('basket').get(pk=pk)
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
            delivery_price = DeliveryCost.objects.only('delivery_express_cost').get(id=1)
            order.totalCost += delivery_price.delivery_express_cost

        order.deliveryType = delivery_type
        order.paymentType = payment_type
        order.city = city
        order.address = address
        order.status = status_order
        order.save()
        return Response({'orderId': order.pk}, status=200)


class TagApiView(APIView):
    def get(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'currentPage'

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': total_pages
        })



class ProductSaleAPIView(APIView):
    def get(self, request):
        sale_products = Product.objects.filter(sale=True).order_by('-id')
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(sale_products, request)
        serializer = ProductSaleSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class ReviewCreateAPIView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.only('id').get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.select_related('author').filter(product=product).order_by('-date')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        try:
            product = Product.objects.only('id').get(pk=id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            profile, _ = Profile.objects.get_or_create(fullName=serializer.validated_data['author'])
            Review.objects.create(
                author=profile,
                email=serializer.validated_data['email'],
                text=serializer.validated_data['text'],
                rate=serializer.validated_data['rate'],
                product=product
            )
            return Response({'detail': 'Review created'}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaymentApiView(APIView):
    def get(self, request, pk):
        payment = get_object_or_404(Payment.objects.select_related('order'), order__id=pk)
        return JsonResponse({'status': payment.order.status})

    def post(self, request, pk):
        data = request.data
        card_number = data['number']
        expiration_month = int(data['month'])
        expiration_year = int(data['year'])
        now_year = datetime.datetime.now().year % 100
        now_month = datetime.datetime.now().month

        if expiration_year < now_year or (expiration_year == now_year and expiration_month < now_month):
            order = Order.objects.only('id').get(id=pk)
            order.payment_error = 'Payment expired'
            order.save()
            return JsonResponse({'error': 'Payment expired'}, status=500)

        if len(card_number.strip()) > 8 and int(card_number) % 2 != 0:
            return JsonResponse({'error': 'Неверный номер банковской карты'})

        res_date = f'{expiration_month}.{expiration_year}'
        order = Order.objects.select_related('basket').get(id=pk)
        payment = Payment.objects.create(order=order, card_number=card_number, validity_period=res_date)
        order.status = 'paid'
        order.save()

        basket = Basket.objects.get(user=request.user)
        basket_items = BasketItems.objects.select_related('product').filter(basket=basket)

        for item in basket_items:
            product = item.product
            if product.count < item.quantity:
                return JsonResponse({'error': 'Недостаточно товаров'}, status=400)
            product.count -= item.quantity
            product.save()
            payment.success = True
            payment.save()
        basket_items.delete()
        return HttpResponse(status=200)

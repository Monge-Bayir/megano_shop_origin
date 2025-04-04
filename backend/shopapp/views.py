from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product
from django.conf import settings

from .models import Category, Subcategory
from .serializers import BannerListSerializer, CatalogListSerializer


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
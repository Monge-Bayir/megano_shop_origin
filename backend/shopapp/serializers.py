from rest_framework import serializers
from .models import Product, Category, Subcategory, Tag, ProductImage, Review, Specification, BasketItems, Order
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        return obj.get_image()


class SubcategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        return obj.get_image()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

    def to_representation(self, instance):
        return {
            'src': instance.image.url,
            'alt': instance.image.name
        }


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['title', 'value']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format='%Y-%m-%d %H:%M')  # формат даты

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']

    def get_author(self, obj):
        return obj.author.fullName


class ProductSaleSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images']

    def get_images(self, obj):
        # Используем метод модели get_image(), чтобы вернуть список изображений
        return obj.get_image()

    def get_dateFrom(self, obj):
        return obj.dateFrom.strftime('%m-%d') if obj.dateFrom else None

    def get_dateTo(self, obj):
        return obj.dateTo.strftime('%m-%d') if obj.dateTo else None



class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategory = SubcategorySerializer()
    tags = TagSerializer(many=True)
    images = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'price', 'count', 'date', 'title',
            'description', 'freeDelivery', 'images', 'tags', 'reviews',
            'specifications', 'rating'
        ]

    def get_images(self, obj):
        return obj.get_image()

    def get_reviews(self, obj):
        reviews = Review.objects.filter(product=obj)
        return ReviewSerializer(reviews, many=True).data

    def get_specifications(self, obj):
        if hasattr(obj, 'specifications'):
            return SpecificationSerializer(obj.specifications.all(), many=True).data
        return []

    def get_rating(self, obj):
        return obj.get_rating()


class ProductShortSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategory = SubcategorySerializer()
    tags = TagSerializer(many=True)
    images = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'price', 'count', 'date', 'title',
            'description', 'freeDelivery', 'images', 'tags', 'reviews',
             'rating'
        ]

    def get_images(self, obj):
        return obj.get_image()

    def get_reviews(self, obj):
        reviews = Review.objects.filter(product=obj)
        return ReviewSerializer(reviews, many=True).data

    def get_rating(self, obj):
        return obj.get_rating()


class CatalogListSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        reviews = Review.objects.filter(product_id=instance.id).values_list(
            'rate', flat=True
        )
        tags = instance.tags.all()

        if reviews.count() == 0:
            rating = 'Отзывов пока нет'
        else:
            rating = round(sum(reviews) / reviews.count(), 2)

        representation['title'] = instance.title
        representation['price'] = instance.price
        representation['images'] = instance.get_image()
        representation['tags'] = [{'id': tag.id, 'title': tag.title} for tag in tags]
        representation['reviews'] = reviews.count()
        representation['rating'] = rating

        return representation

class BannerListSerializer(CatalogListSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        tags = instance.tags.all()
        rep['tags'] = [tag.title for tag in tags]
        return rep


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItems
        fields = (
            'product', 'count'
        )

    def to_representation(self, instance):
        data = ProductShortSerializer(instance.product).data
        data['count'] = instance.quantity
        return data


class OrderSerializers(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'created_at', 'fullName', 'email', 'phone',
            'deliveryType', 'paymentType', 'totalCost', 'status',
            'city', 'address', 'products', 'basket'
        ]

    def get_products(self, obj):
        basket_items = BasketItems.objects.filter(basket=obj.basket)
        return [
            {
                'id': item.product.id,
                'category': item.product.category.id if item.product.category else None,
                'price': item.product.price,
                'count': item.product.count,
                'date': item.product.date.strftime('%Y.%m.%d %H:%M'),
                'title': item.product.title,
                'description': item.product.description,
                'freeDelivery': item.product.freeDelivery,
                'images': item.product.get_image(),
                'tags': [tag.title for tag in item.product.tags.all()],
                'rating': float(item.product.get_rating())
            }
            for item in basket_items
        ]

    def create(self, validated_data):
        basket = validated_data.get('basket')
        order = Order.objects.create(**validated_data)

        basket_items = BasketItems.objects.filter(basket=basket)
        for item in basket_items:
            order.products.add(item.product)

        return order


class Tags(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']





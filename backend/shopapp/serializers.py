from rest_framework import serializers
from .models import Product, Review, Tag

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
from django.contrib import admin
from .models import Category, Subcategory, Product, ProductImage, Review, Specification, Tag, BasketItems, Basket

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Specification)
admin.site.register(Tag)
admin.site.register(Basket)
admin.site.register(BasketItems)
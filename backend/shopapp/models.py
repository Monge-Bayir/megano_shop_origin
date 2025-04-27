from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from userauth.models import Profile
from django.contrib.auth.models import User

def upload_image_category_path(instance: 'Category', filename: str) -> str:
    return f'categories/category_{instance.pk}/images/{filename}'

class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to=upload_image_category_path)

    def get_image(self):
        image = {
            'src': self.image.url,
            'alt': self.image.name
        }
        return image


def upload_image_category_path(instance: 'Subcategory', filename: str) -> str:
    return f'categories/subcategory_{instance.pk}/images/{filename}'

class Subcategory(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to=upload_image_category_path)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def get_image(self):
        image = {
            'src': self.image.url,
            'alt': self.image.name
        }
        return image


class Specification(models.Model):
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=50, null=True, blank=True)


class Tag(models.Model):
    title = models.CharField(max_length=100)


def upload_preview_product_path(instance: 'Product', filename: str) -> str:
    return f'products/product_{instance.pk}/images/{filename}'

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True, blank=True)
    freeDelivery = models.BooleanField(default=True)
    preview = models.ImageField(null=True, blank=True, upload_to=upload_preview_product_path)
    tags = models.ManyToManyField(Tag)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    specifications = models.ManyToManyField(Specification, blank=True)

    sale = models.BooleanField(default=False)
    salePrice = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dateFrom = models.DateField(null=True, blank=True)
    dateTo = models.DateField(null=True, blank=True)

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def get_image(self):
        images = ProductImage.objects.filter(product_id=self.pk)
        return [
            {'src': image.image.url, 'alt': image.image.name} for image in images
        ]

    def get_rating(self):
        reviews = Review.objects.filter(product_id=self.pk).values_list(
            'rate', flat=True
        )
        if reviews.count() == 0:
            rating = 0
            return rating
        rating = sum(reviews) / reviews.count()
        return rating


class Review(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    email = models.EmailField(default='example@mail.ru')
    text = models.TextField(max_length=1500)
    rate = models.PositiveIntegerField(
        validators=[MaxValueValidator(5)]
    )
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


from django.db import models
import uuid
from django.contrib.auth.models import User

class Basket(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Basket for {self.user}"
        else:
            return f"Basket for session {self.session_id}"

    def save(self, *args, **kwargs):
        if not self.user and not self.session_id:
            self.session_id = str(uuid.uuid4())  # Генерация уникального ID для сессии
        super().save(*args, **kwargs)


class BasketItems(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Предполагается, что у вас есть модель Product
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"



class Order(models.Model):
    delivery_choice = (
        ('express', 'Экспресс-доставка'),
        ('delivery', 'Обычная доставка'),
    )

    payment_choice = (
        ('online', 'Онлайн оплата'),
        ('inCash', 'Наличными'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=100)
    email = models.EmailField(default='example@mail.ru')
    phone = models.CharField(max_length=13)
    deliveryType = models.CharField(max_length=100, choices=delivery_choice)
    paymentType = models.CharField(max_length=20, choices=payment_choice)
    totalCost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    status = models.CharField(max_length=100, default='Processing...')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    products = models.ManyToManyField(Product)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, default=None)
    payment_error = models.CharField(max_length=200, blank=True)


class DeliveryCost(models.Model):
    delivery_cost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    delivery_express_cost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    delivery_free_min = models.DecimalField(default=0, max_digits=8, decimal_places=2) #наименьшая сумма для бесплатной доставки


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    validity_period = models.CharField(max_length=20)
    success = models.BooleanField(default=False)


def upload_image_saleproduct_path(instance: 'SaleItem', filename: str):
    return f'saleproducts/product_{instance.pk}/image/{filename}'

class SaleItem(models.Model):
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    salePrice = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    dateFrom = models.DateTimeField(null=True, blank=True)
    dateTo = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=100)
    preview = models.ImageField(null=True, blank=True, upload_to=upload_image_saleproduct_path)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_image(self):
        images = ProductImage.objects.filter(product_id=self.pk)
        return [
            {'src': image.image.url, 'alt': image.image.name} for image in images
        ]


def upload_product_image_path(instance: 'Product', filename: str) -> str:
    return f'products/product_{instance.product.pk}/images/{filename}'

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=CASCADE
    )
    image = models.ImageField(upload_to=upload_product_image_path)
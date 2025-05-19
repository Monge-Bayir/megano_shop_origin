from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Category, Subcategory, Product, Tag, Specification,
    Basket, BasketItems, Order, DeliveryCost, Review, ProductImage
)
from userauth.models import Profile
from decimal import Decimal

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = Profile.objects.create(user=self.user, fullName='Test User')
        self.category = Category.objects.create(title='Electronics')
        self.subcategory = Subcategory.objects.create(title='Phones', category=self.category)
        self.tag = Tag.objects.create(title='New')
        self.spec = Specification.objects.create(title='Color', value='Black')
        self.product = Product.objects.create(
            category=self.category,
            title='iPhone',
            price=Decimal('999.99'),
            count=10,
            subcategory=self.subcategory
        )
        self.product.tags.add(self.tag)
        self.product.specifications.add(self.spec)

    def test_subcategory_creation(self):
        self.assertEqual(str(self.subcategory.title), 'Phones')
        self.assertEqual(self.subcategory.category, self.category)

    def test_product_creation(self):
        self.assertEqual(self.product.title, 'iPhone')
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertIn(self.tag, self.product.tags.all())
        self.assertIn(self.spec, self.product.specifications.all())

    def test_basket_creation_for_user(self):
        basket = Basket.objects.create(user=self.user)
        self.assertEqual(basket.user, self.user)

    def test_add_product_to_basket(self):
        basket = Basket.objects.create(user=self.user)
        item = BasketItems.objects.create(basket=basket, product=self.product, quantity=3)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 3)

    def test_order_creation(self):
        basket = Basket.objects.create(user=self.user)
        item = BasketItems.objects.create(basket=basket, product=self.product, quantity=2)
        delivery = DeliveryCost.objects.create(delivery_cost=50, delivery_free_min=500)
        order = Order.objects.create(
            fullName='Test User',
            email='test@example.com',
            phone='1234567890',
            deliveryType='delivery',
            paymentType='online',
            totalCost=Decimal('1000.00'),
            city='TestCity',
            address='TestStreet 1',
            basket=basket
        )
        order.products.add(self.product)
        self.assertEqual(order.basket, basket)
        self.assertIn(self.product, order.products.all())

    def test_review_creation_and_rating(self):
        Review.objects.create(
            author=self.profile,
            product=self.product,
            text='Great phone!',
            rate=5,
            email='test@example.com'
        )
        self.assertEqual(self.product.get_rating(), 5)

    def test_rating_average_multiple_reviews(self):
        Review.objects.create(author=self.profile, product=self.product, rate=5, text='Nice', email='a@mail.com')
        Review.objects.create(author=self.profile, product=self.product, rate=3, text='Ok', email='b@mail.com')
        self.assertAlmostEqual(self.product.get_rating(), 4.0)


    def test_sale_price_and_discount_logic(self):
        self.product.sale = True
        self.product.salePrice = Decimal('799.99')
        self.product.save()
        self.assertTrue(self.product.sale)
        self.assertEqual(self.product.salePrice, Decimal('799.99'))

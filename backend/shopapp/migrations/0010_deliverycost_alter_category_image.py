# Generated by Django 5.2 on 2025-04-16 09:55

import shopapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0009_order_basket_order_payment_error_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_cost', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('delivery_express_cost', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('delivery_free_min', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
            ],
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=shopapp.models.upload_image_category_path),
        ),
    ]

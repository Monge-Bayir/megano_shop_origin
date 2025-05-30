# Generated by Django 5.2 on 2025-04-16 09:32

import django.db.models.deletion
import shopapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0008_alter_category_image_alter_order_paymenttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='basket',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='shopapp.basket'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_error',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=shopapp.models.upload_image_category_path),
        ),
    ]

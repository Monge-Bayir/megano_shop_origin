# Generated by Django 5.2 on 2025-04-16 10:35

import shopapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0012_alter_category_image_alter_order_basket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='basket',
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=shopapp.models.upload_image_category_path),
        ),
    ]

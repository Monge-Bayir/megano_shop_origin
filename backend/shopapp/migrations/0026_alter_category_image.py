# Generated by Django 5.2 on 2025-04-27 16:21

import shopapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0025_alter_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=shopapp.models.upload_image_category_path),
        ),
    ]

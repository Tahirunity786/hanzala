# Generated by Django 5.0.1 on 2024-01-17 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_userproducts_images_productimage_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproducts',
            name='product_token',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=200, null=True),
        ),
    ]

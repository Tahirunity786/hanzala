# Generated by Django 5.0.1 on 2024-02-03 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_order_address1_order_address2_order_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproducts',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userproducts',
            name='total_price',
            field=models.IntegerField(default=0),
        ),
    ]

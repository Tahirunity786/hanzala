# Generated by Django 5.0.1 on 2024-01-26 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_order_purchased_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='review_at_product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reviews_at_product', to='core.userproducts'),
        ),
        migrations.AddField(
            model_name='reviews',
            name='review_given_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='reviews',
            name='reviews',
            field=models.IntegerField(default=0),
        ),
    ]
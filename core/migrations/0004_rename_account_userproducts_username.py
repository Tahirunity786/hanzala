# Generated by Django 5.0.1 on 2024-01-17 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_userproducts_product_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userproducts',
            old_name='account',
            new_name='username',
        ),
    ]

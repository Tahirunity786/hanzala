# Generated by Django 5.0.1 on 2024-02-04 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userproducts',
            name='user_image',
        ),
    ]
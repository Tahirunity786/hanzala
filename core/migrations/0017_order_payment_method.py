# Generated by Django 5.0.1 on 2024-01-28 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_info_user_address2'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(db_index=True, default=False, max_length=100),
        ),
    ]

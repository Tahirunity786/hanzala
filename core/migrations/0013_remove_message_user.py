# Generated by Django 5.0.1 on 2024-01-27 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_message_is_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
    ]

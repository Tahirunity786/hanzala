# Generated by Django 5.0.1 on 2024-02-02 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(db_index=True, default=None, max_length=200),
        ),
    ]
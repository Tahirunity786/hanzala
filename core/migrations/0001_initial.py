# Generated by Django 5.0.1 on 2024-02-04 08:21

import core.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='product_images/', verbose_name='Product Image')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('profile', models.ImageField(blank=True, null=True, upload_to='profile/images')),
                ('full_name', models.CharField(max_length=100)),
                ('username', models.CharField(db_index=True, max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(default=None, null=True)),
                ('is_blocked', models.BooleanField(default=False, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_seller', models.BooleanField(default=False)),
                ('is_buyer', models.BooleanField(default=False)),
                ('password', models.CharField(db_index=True, default=None, max_length=200)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(db_index=True, default=False, max_length=100)),
                ('content', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(default=None, max_length=100)),
                ('user_image', models.ImageField(default=core.models.UserProducts.default_user_image, upload_to='product_images/user', verbose_name='Product user Image')),
                ('product_token', models.CharField(blank=True, db_index=True, default=None, max_length=200, null=True)),
                ('product_title', models.CharField(db_index=True, default=None, max_length=150)),
                ('product_description', models.TextField(default=None, verbose_name='Product Description')),
                ('product_address', models.TextField(default=None, verbose_name='Product address')),
                ('condition', models.CharField(default='Not decided', max_length=20, verbose_name='Condition')),
                ('brand', models.CharField(db_index=True, default='Not decided', max_length=100, verbose_name='Brand')),
                ('color', models.CharField(default=None, max_length=100)),
                ('model', models.CharField(default=None, max_length=100)),
                ('ram', models.CharField(default=None, max_length=100)),
                ('storage', models.BigIntegerField(default=0)),
                ('battery_capacity', models.CharField(default=None, max_length=20)),
                ('price', models.IntegerField(default=None)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('latitude', models.CharField(db_index=True, default=False, max_length=100)),
                ('longitude', models.CharField(db_index=True, default=False, max_length=100)),
                ('notification_token', models.CharField(db_index=True, default=False, max_length=200)),
                ('total_price', models.IntegerField(default=0)),
                ('quantity', models.IntegerField(default=1, null=True)),
                ('is_sold', models.BooleanField(default=False)),
                ('product_image', models.ManyToManyField(blank=True, related_name='products_images', to='core.productimage')),
                ('username', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User Products',
            },
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviews', models.IntegerField(default=0)),
                ('reviewer_message', models.TextField(verbose_name='Message')),
                ('review_given_at', models.DateTimeField(auto_now=True)),
                ('reviews_giver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_given', to=settings.AUTH_USER_MODEL)),
                ('review_at_product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews_at_product', to='core.userproducts')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('activate_order', models.CharField(db_index=True, default=False, max_length=100)),
                ('received_order', models.CharField(db_index=True, default=False, max_length=100)),
                ('canceled_order', models.CharField(db_index=True, default=False, max_length=100)),
                ('total_price', models.IntegerField(default=0)),
                ('payment_method', models.CharField(db_index=True, default=False, max_length=100)),
                ('full_name', models.CharField(db_index=True, default=False, max_length=100, null=True)),
                ('payment_intent_id', models.CharField(db_index=True, default=False, max_length=100, null=True)),
                ('country', models.CharField(db_index=True, default=False, max_length=100, null=True)),
                ('address1', models.TextField(null=True)),
                ('address2', models.TextField(null=True)),
                ('postal_code', models.IntegerField(default=0, null=True)),
                ('latitude1', models.CharField(db_index=True, default=False, max_length=100, null=True)),
                ('latitude2', models.CharField(db_index=True, default=False, max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userproducts')),
            ],
        ),
        migrations.CreateModel(
            name='FavouritesSaved',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='core.userproducts')),
            ],
            options={
                'verbose_name': 'Favorite Saved',
                'verbose_name_plural': 'Favorites Saved',
                'ordering': ['-saved_at'],
            },
        ),
    ]

# Generated by Django 4.2.10 on 2024-03-21 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('image', models.ImageField(null=True, upload_to='users/images')),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=64)),
                ('national_code', models.CharField(max_length=10, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('manager', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
    ]

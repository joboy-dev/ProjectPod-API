# Generated by Django 5.0.1 on 2024-01-25 20:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_blacklistedtoken_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='blacklistedtoken',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='blacklistedtoken',
            name='token',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]

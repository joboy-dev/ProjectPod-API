# Generated by Django 5.0.1 on 2024-01-24 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_customuser_verification_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='verification_token',
        ),
    ]
# Generated by Django 4.1.13 on 2024-04-14 17:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0007_alter_task_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 14, 18, 50, 59, 95374)),
        ),
    ]

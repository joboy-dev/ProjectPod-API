# Generated by Django 5.0.1 on 2024-04-19 18:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0029_alter_project_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 19, 19, 53, 56, 916495)),
        ),
    ]

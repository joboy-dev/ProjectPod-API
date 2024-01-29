# Generated by Django 5.0.1 on 2024-01-27 11:34

import datetime
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('workspace', '0010_alter_member_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=255)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2024, 1, 27, 12, 34, 26, 222484))),
                ('end_date', models.DateTimeField(null=True)),
                ('members', models.ManyToManyField(blank=True, related_name='projects', to='workspace.member')),
                ('workspaace', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='workspace.workspace')),
            ],
        ),
    ]

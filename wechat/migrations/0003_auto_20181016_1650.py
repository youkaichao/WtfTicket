# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-10-16 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0002_auto_20160502_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='student_id',
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]

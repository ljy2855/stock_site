# Generated by Django 2.0.13 on 2021-01-05 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20210105_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='author',
        ),
        migrations.RemoveField(
            model_name='post',
            name='post_stock',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-09 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20210105_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockdata',
            name='pre_price',
            field=models.IntegerField(default=0),
        ),
    ]

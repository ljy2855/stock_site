# Generated by Django 4.2.7 on 2023-11-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='current_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stock',
            name='high_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stock',
            name='low_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stock',
            name='up_down',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stock',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

# Generated by Django 3.0.8 on 2020-08-09 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingApp', '0006_roomtype_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='days',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='total_payment',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

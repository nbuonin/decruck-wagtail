# Generated by Django 3.0.8 on 2020-07-10 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20200709_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='genre_en',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='genre',
            name='genre_fr',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='instrument',
            name='instrument_en',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='instrument',
            name='instrument_fr',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
# Generated by Django 3.0.8 on 2020-08-15 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20200815_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositionpage',
            name='genre_temp',
            field=models.ManyToManyField(blank=True, null=True, related_name='compositions', to='main.Genre'),
        ),
        migrations.AddField(
            model_name='scorepage',
            name='genre_temp',
            field=models.ManyToManyField(blank=True, null=True, related_name='scores', to='main.Genre'),
        ),
    ]

# Generated by Django 2.2.12 on 2020-06-23 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20200531_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitemlink',
            name='access_ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]

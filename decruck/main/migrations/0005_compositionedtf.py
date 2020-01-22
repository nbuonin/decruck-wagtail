# Generated by Django 2.2.9 on 2020-01-20 17:14

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20191228_1826'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompositionEDTF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edtf_string', models.CharField(max_length=256, verbose_name='Date')),
                ('lower_fuzzy', models.DateField(editable=False)),
                ('upper_fuzzy', models.DateField(editable=False)),
                ('lower_strict', models.DateField(editable=False)),
                ('upper_strict', models.DateField(editable=False)),
                ('composition', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='date', to='main.CompositionPage', unique=True)),
            ],
        ),
    ]

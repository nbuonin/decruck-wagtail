# Generated by Django 2.2.12 on 2020-05-24 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_remove_scorepage_preview_score_checksum'),
    ]

    operations = [
        migrations.AddField(
            model_name='scorepage',
            name='preview_score_checksum',
            field=models.CharField(blank=True, editable=False, max_length=256),
        ),
    ]
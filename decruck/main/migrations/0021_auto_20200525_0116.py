# Generated by Django 2.2.12 on 2020-05-25 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_scorepage_preview_score_checksum'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='previewscoreimage',
            options={'ordering': ['page_number']},
        ),
        migrations.AlterField(
            model_name='previewscoreimage',
            name='score',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preview_score_images', to='main.ScorePage'),
        ),
    ]
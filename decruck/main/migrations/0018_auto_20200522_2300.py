# Generated by Django 2.2.12 on 2020-05-22 23:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20200522_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='scorepage',
            name='preview_score_checksum',
            field=models.CharField(blank=True, editable=False, max_length=256),
        ),
        migrations.CreateModel(
            name='PreviewScoreImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preview_score_image', models.ImageField(upload_to='score_preview_images/')),
                ('page_number', models.PositiveSmallIntegerField()),
                ('score', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ScorePage')),
            ],
            options={
                'unique_together': {('score', 'page_number')},
            },
        ),
    ]

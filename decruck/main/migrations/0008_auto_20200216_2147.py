# Generated by Django 2.2.10 on 2020-02-16 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20200212_0232'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.CharField(max_length=256)),
            ],
        ),
        migrations.AlterField(
            model_name='compositionpage',
            name='genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='main.Genre'),
        ),
        migrations.AlterField(
            model_name='scorepage',
            name='genre',
            field=models.CharField(blank=True, choices=[('ARRANGEMENTS', 'Arrangements'), ('CHAMBER', 'Chamber Music'), ('ETUDES', 'Etudes'), ('ORCHESTRAL', 'Orchestral Music'), ('ORGAN', 'Organ Music'), ('SOLO_PIANO', 'Solo Piano Music'), ('ART_SONG', 'Art Song'), ('CHORAL', 'Choral')], max_length=256),
        ),
    ]

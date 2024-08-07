# Generated by Django 3.0.11 on 2020-12-30 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_auto_20201229_0335'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositionpage',
            name='edtf_string',
            field=models.CharField(blank=True, help_text='A date in the <a href="https://www.loc.gov/standards/datetime/" target="_blank"><strong>Extended Date Time Format</strong></a>', max_length=256, verbose_name='EDTF Date'),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='lower_fuzzy',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='lower_strict',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='nat_lang_edtf_string',
            field=models.CharField(blank=True, help_text="The EDTF date in natural language. This field is help users who aren't familiar with the EDTF. It does not change how the date is represented.", max_length=256, verbose_name='Natural Language Date'),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='nat_lang_year',
            field=models.CharField(blank=True, editable=False, max_length=9),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='upper_fuzzy',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='upper_strict',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
    ]

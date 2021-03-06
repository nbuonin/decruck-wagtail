# Generated by Django 2.2.9 on 2020-02-12 02:32

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20200122_1520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compositionpage',
            old_name='orchestral_instrumentation',
            new_name='orchestration',
        ),
        migrations.RemoveField(
            model_name='compositionpage',
            name='recording_link',
        ),
        migrations.AddField(
            model_name='compositionpage',
            name='recording',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())], blank=True),
        ),
        migrations.AlterField(
            model_name='compositionedtf',
            name='edtf_string',
            field=models.CharField(help_text='A date in the <a href="https://www.loc.gov/standards/datetime/" target="_blank"><strong>Extended Date Time Format</strong></a>', max_length=256, verbose_name='EDTF Date'),
        ),
        migrations.AlterField(
            model_name='compositionedtf',
            name='nat_lang_edtf_string',
            field=models.CharField(help_text="The EDTF date in natural language. This field is help users who aren't familiar with the EDTF. It does not change how the date is represented.", max_length=256, verbose_name='Natural Language Date'),
        ),
    ]

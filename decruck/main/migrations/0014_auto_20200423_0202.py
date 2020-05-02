# Generated by Django 2.2.12 on 2020-04-23 02:02

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20200423_0156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biographypage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())])), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())]))])), ('block_quote', wagtail.core.blocks.BlockQuoteBlock())]),
        ),
        migrations.AlterField(
            model_name='biographypage',
            name='body_en',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())])), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())]))])), ('block_quote', wagtail.core.blocks.BlockQuoteBlock())], null=True),
        ),
        migrations.AlterField(
            model_name='biographypage',
            name='body_fr',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())])), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())]))])), ('block_quote', wagtail.core.blocks.BlockQuoteBlock())], null=True),
        ),
    ]

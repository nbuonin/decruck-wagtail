# Generated by Django 3.0.8 on 2020-07-17 02:19

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20200710_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biographypage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())], icon='bold', template='main/blocks/bio-heading.html')), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))]))], icon='pilcrow', template='main/blocks/bio-row.html')), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.CharBlock()), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic']))], icon='openquote', template='main/blocks/bio-quote.html'))]),
        ),
        migrations.AlterField(
            model_name='biographypage',
            name='body_en',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())], icon='bold', template='main/blocks/bio-heading.html')), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))]))], icon='pilcrow', template='main/blocks/bio-row.html')), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.CharBlock()), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic']))], icon='openquote', template='main/blocks/bio-quote.html'))], null=True),
        ),
        migrations.AlterField(
            model_name='biographypage',
            name='body_fr',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.CharBlock()), ('right_column', wagtail.core.blocks.CharBlock())], icon='bold', template='main/blocks/bio-heading.html')), ('row', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))])), ('right_column', wagtail.core.blocks.StreamBlock([('rich_text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link', 'embed'])), ('caption_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('image_max_width', wagtail.core.blocks.IntegerBlock()), ('caption', wagtail.core.blocks.CharBlock())], icon='image', template='main/blocks/bio-caption-image.html'))]))], icon='pilcrow', template='main/blocks/bio-row.html')), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.CharBlock()), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic']))], icon='openquote', template='main/blocks/bio-quote.html'))], null=True),
        ),
    ]

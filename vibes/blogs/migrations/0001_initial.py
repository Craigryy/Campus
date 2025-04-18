# Generated by Django 4.2.20 on 2025-03-18 10:36

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.routable_page.models
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0094_alter_page_locale'),
        ('wagtailimages', '0026_delete_uploadedimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Category name', max_length=255)),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name_plural': 'Blog Categories',
            },
        ),
        migrations.CreateModel(
            name='BlogPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('date', models.DateField(verbose_name='Post date')),
                ('featured', models.BooleanField(default=False, help_text='Mark as a featured story')),
                ('content', wagtail.fields.StreamField([('video', 3), ('image', 7)], blank=True, block_lookup={0: ('wagtail.blocks.CharBlock', (), {'help_text': 'Title of the video', 'required': True}), 1: ('wagtail.blocks.TextBlock', (), {'help_text': 'Short description of the video', 'required': False}), 2: ('wagtail.documents.blocks.DocumentChooserBlock', (), {'help_text': 'Upload a video file'}), 3: ('wagtail.blocks.StructBlock', [[('title', 0), ('description', 1), ('file', 2)]], {'icon': 'media', 'label': 'Video'}), 4: ('wagtail.blocks.CharBlock', (), {'help_text': 'Title of the image', 'required': True}), 5: ('wagtail.blocks.TextBlock', (), {'help_text': 'Short description of the image', 'required': False}), 6: ('wagtail.images.blocks.ImageChooserBlock', (), {'icon': 'image', 'label': 'Image'}), 7: ('wagtail.blocks.StructBlock', [[('title', 4), ('description', 5), ('image', 6)]], {'icon': 'image', 'label': 'Image'})})),
                ('categories', modelcluster.fields.ParentalManyToManyField(blank=True, to='blogs.blogcategory')),
            ],
            options={
                'verbose_name': 'Blog Page',
                'verbose_name_plural': 'Blog Pages',
            },
            bases=(wagtail.contrib.routable_page.models.RoutablePageMixin, 'wagtailcore.page'),
        ),
    ]

# Generated by Django 4.2.20 on 2025-03-17 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_upcomingevent_alter_homepage_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upcomingevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

# Generated by Django 4.0.8 on 2022-11-11 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_pagereadlogs_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='other',
        ),
        migrations.RemoveField(
            model_name='event',
            name='references',
        ),
    ]

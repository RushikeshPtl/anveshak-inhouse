# Generated by Django 4.0.8 on 2022-11-04 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_saved',
            field=models.BooleanField(default=1),
        ),
        migrations.AddField(
            model_name='event',
            name='is_submitted',
            field=models.BooleanField(default=0),
        ),
    ]
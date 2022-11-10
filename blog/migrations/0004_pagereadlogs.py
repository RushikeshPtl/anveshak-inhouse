# Generated by Django 4.0.8 on 2022-11-07 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_event_other_event_references'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageReadLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.IntegerField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.event')),
            ],
        ),
    ]
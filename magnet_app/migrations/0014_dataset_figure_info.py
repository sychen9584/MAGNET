# Generated by Django 3.0.3 on 2022-01-21 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_app', '0013_exampledata_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='figure_info',
            field=models.TextField(blank=True),
        ),
    ]

# Generated by Django 3.0.3 on 2021-02-12 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_app', '0007_auto_20210206_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='graph_edge',
            name='overlap_num',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]

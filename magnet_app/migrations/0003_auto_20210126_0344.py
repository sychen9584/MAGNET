# Generated by Django 3.0.3 on 2021-01-26 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_app', '0002_auto_20200417_0350'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='gene',
            name='magnet_app__ensembl_ec96af_idx',
        ),
        migrations.AddIndex(
            model_name='gene',
            index=models.Index(fields=['ensembl_id', 'gene_symbol'], name='magnet_app__ensembl_210ff0_idx'),
        ),
    ]

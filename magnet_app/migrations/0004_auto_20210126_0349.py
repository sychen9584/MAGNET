# Generated by Django 3.0.3 on 2021-01-26 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_app', '0003_auto_20210126_0344'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='gene',
            name='magnet_app__ensembl_210ff0_idx',
        ),
        migrations.AddIndex(
            model_name='gene',
            index=models.Index(fields=['ensembl_id'], name='magnet_app__ensembl_ec96af_idx'),
        ),
        migrations.AddIndex(
            model_name='gene',
            index=models.Index(fields=['gene_symbol'], name='magnet_app__gene_sy_befde2_idx'),
        ),
    ]

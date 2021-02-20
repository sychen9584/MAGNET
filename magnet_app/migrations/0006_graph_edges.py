# Generated by Django 3.0.3 on 2021-02-06 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_app', '0005_auto_20210126_0420'),
    ]

    operations = [
        migrations.CreateModel(
            name='Graph_edges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proportion', models.FloatField()),
                ('cluster1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cluster1', to='magnet_app.Cluster')),
                ('cluster2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cluster2', to='magnet_app.Cluster')),
            ],
        ),
    ]

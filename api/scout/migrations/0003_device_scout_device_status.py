# Generated by Django 4.2.9 on 2024-03-01 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scout', '0002_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='scout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scout.scout'),
        ),
        migrations.AddField(
            model_name='device',
            name='status',
            field=models.IntegerField(choices=[(0, 'AVAILABLE'), (1, 'ACTIVE'), (2, 'CHALLLENGE REQUIRED')], default=0),
        ),
    ]

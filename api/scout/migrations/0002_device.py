# Generated by Django 4.2.9 on 2024-03-01 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('id', models.CharField(db_index=True, max_length=255, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('app_version', models.CharField(max_length=10)),
                ('android_version', models.IntegerField()),
                ('android_release', models.CharField(max_length=5)),
                ('dpi', models.CharField(max_length=7)),
                ('resolution', models.CharField(max_length=10)),
                ('manufacturer', models.CharField(max_length=20)),
                ('device', models.CharField(max_length=12)),
                ('model', models.CharField(max_length=12)),
                ('cpu', models.CharField(max_length=10)),
                ('version_code', models.CharField(max_length=12)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

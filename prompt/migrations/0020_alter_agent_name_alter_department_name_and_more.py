# Generated by Django 5.0.6 on 2024-06-17 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prompt', '0019_alter_prompt_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='name',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=1024),
        ),
    ]

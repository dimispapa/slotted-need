# Generated by Django 5.1 on 2024-09-11 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_component_measurement_unit_componentpart'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentpart',
            name='slug',
            field=models.SlugField(default='', unique=True),
            preserve_default=False,
        ),
    ]

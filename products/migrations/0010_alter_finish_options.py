# Generated by Django 5.1 on 2024-09-03 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_component_finishes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='finish',
            options={'ordering': ['name'], 'verbose_name_plural': 'Finishes'},
        ),
    ]

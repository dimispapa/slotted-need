# Generated by Django 5.1 on 2024-09-03 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_product_components_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FinishOptionValue',
        ),
    ]
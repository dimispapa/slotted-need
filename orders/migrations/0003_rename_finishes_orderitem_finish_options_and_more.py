# Generated by Django 5.1 on 2024-09-07 09:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='finishes',
            new_name='finish_options',
        ),
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=7, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
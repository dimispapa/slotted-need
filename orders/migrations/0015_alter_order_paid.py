# Generated by Django 5.1 on 2024-09-20 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid',
            field=models.IntegerField(choices=[(1, 'Not Paid'), (2, 'Fully Paid')], default=1),
        ),
    ]
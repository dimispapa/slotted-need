# Generated by Django 5.1 on 2024-09-20 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_paid_orderitem_item_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid',
            field=models.IntegerField(choices=[(1, 'Not Fully Paid'), (2, 'Fully Paid')], default=1),
        ),
    ]

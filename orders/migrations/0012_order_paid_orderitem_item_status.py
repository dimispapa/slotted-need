# Generated by Django 5.1 on 2024-09-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_alter_componentfinish_options_delete_optionfinish'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='item_status',
            field=models.IntegerField(choices=[(1, 'Not Started'), (2, 'In Progress'), (3, 'Made'), (4, 'Delivered')], default=1),
        ),
    ]

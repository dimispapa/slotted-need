# Generated by Django 5.1 on 2024-10-03 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_orderitem_priority_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]

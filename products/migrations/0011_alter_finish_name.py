# Generated by Django 5.1 on 2024-09-03 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_finish_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finish',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]

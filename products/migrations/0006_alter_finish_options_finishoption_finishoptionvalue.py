# Generated by Django 5.1 on 2024-09-02 13:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_finish_alter_optionvalue_value_product_finishes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='finish',
            options={'verbose_name_plural': 'Finishes'},
        ),
        migrations.CreateModel(
            name='FinishOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('finish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='products.finish')),
            ],
        ),
        migrations.CreateModel(
            name='FinishOptionValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('finish_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='products.finishoption')),
            ],
        ),
    ]

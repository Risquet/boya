# Generated by Django 4.2.6 on 2024-04-05 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_data_errors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='value',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

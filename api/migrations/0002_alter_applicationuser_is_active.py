# Generated by Django 4.2.6 on 2024-03-04 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationuser',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='Activo'),
        ),
    ]

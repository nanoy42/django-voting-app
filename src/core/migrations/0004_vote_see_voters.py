# Generated by Django 3.1.4 on 2021-02-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201204_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='see_voters',
            field=models.BooleanField(default=False, verbose_name='see voters'),
        ),
    ]

# Generated by Django 2.2.3 on 2019-08-01 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasureHunt', '0003_auto_20190731_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='description',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='title',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]

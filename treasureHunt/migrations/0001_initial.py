# Generated by Django 2.2.3 on 2019-07-30 23:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('current_room', models.IntegerField(default=0)),
                ('cooldown', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('explore_mode', models.BooleanField(default=False)),
                ('encumbrance', models.IntegerField(default=0)),
                ('speed', models.IntegerField(default=0)),
                ('gold', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('room_id', models.IntegerField()),
                ('coord_x', models.SmallIntegerField(blank=True)),
                ('coord_y', models.SmallIntegerField(blank=True)),
                ('elevation', models.IntegerField(blank=True)),
                ('terrain', models.CharField(blank=True, max_length=255)),
                ('n_to', models.IntegerField(default=0)),
                ('s_to', models.IntegerField(default=0)),
                ('e_to', models.IntegerField(default=0)),
                ('w_to', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

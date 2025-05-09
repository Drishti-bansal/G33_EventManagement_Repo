# Generated by Django 5.2 on 2025-04-16 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('datein', models.DateField()),
                ('dateout', models.DateField()),
                ('Room', models.IntegerField()),
                ('price', models.IntegerField()),
                ('members', models.IntegerField()),
                ('special', models.TextField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

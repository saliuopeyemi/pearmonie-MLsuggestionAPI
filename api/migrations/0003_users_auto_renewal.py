# Generated by Django 5.1.7 on 2025-03-24 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='auto_renewal',
            field=models.BooleanField(default=False),
        ),
    ]

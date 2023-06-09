# Generated by Django 4.1.8 on 2023-05-21 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0005_alter_notification_broadcast_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitems',
            name='is_seen',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='receiver',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]

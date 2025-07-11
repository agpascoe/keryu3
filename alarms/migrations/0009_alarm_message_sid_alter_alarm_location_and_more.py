# Generated by Django 5.0.2 on 2025-04-09 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alarms", "0008_alter_alarm_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="alarm",
            name="message_sid",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="alarm",
            name="location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="alarm",
            name="notification_status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PROCESSING", "Processing"),
                    ("ACCEPTED", "Accepted"),
                    ("SENT", "Sent"),
                    ("DELIVERED", "Delivered"),
                    ("FAILED", "Failed"),
                    ("ERROR", "Error"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="alarm",
            name="whatsapp_message_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="notificationattempt",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PROCESSING", "Processing"),
                    ("ACCEPTED", "Accepted"),
                    ("SENT", "Sent"),
                    ("DELIVERED", "Delivered"),
                    ("FAILED", "Failed"),
                    ("ERROR", "Error"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
    ]

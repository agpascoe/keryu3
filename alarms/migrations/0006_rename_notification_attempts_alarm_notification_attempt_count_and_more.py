# Generated by Django 5.0.2 on 2025-04-08 15:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alarms", "0005_add_resolution_fields_and_notification_attempt"),
        ("custodians", "0006_alter_custodian_verification_code_timestamp"),
        ("subjects", "0007_delete_alarm"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="alarm",
            old_name="notification_attempts",
            new_name="notification_attempt_count",
        ),
        migrations.AddIndex(
            model_name="alarm",
            index=models.Index(fields=["resolved_at"], name="alarms_resolved_at_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationattempt",
            index=models.Index(
                fields=["alarm", "channel"], name="notif_alarm_channel_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="notificationattempt",
            index=models.Index(fields=["status"], name="notif_status_idx"),
        ),
    ]

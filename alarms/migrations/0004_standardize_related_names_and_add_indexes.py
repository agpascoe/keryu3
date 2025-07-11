# Generated by Django 5.0.2 on 2025-04-08 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alarms", "0003_alarm_description_alarm_issue_type"),
    ]

    operations = [
        # Add database indexes
        migrations.AddIndex(
            model_name="alarm",
            index=models.Index(fields=["timestamp"], name="alarms_timestamp_idx"),
        ),
        migrations.AddIndex(
            model_name="alarm",
            index=models.Index(fields=["notification_status"], name="alarms_status_idx"),
        ),
        migrations.AddIndex(
            model_name="alarm",
            index=models.Index(fields=["subject", "timestamp"], name="alarms_subject_timestamp_idx"),
        ),
        
        # Update related names
        migrations.AlterField(
            model_name="alarm",
            name="subject",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="alarms",
                to="subjects.subject",
            ),
        ),
        migrations.AlterField(
            model_name="alarm",
            name="qr_code",
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="alarms",
                to="subjects.subjectqr",
            ),
        ),
    ] 
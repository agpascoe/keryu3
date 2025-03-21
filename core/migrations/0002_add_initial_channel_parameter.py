from django.db import migrations

def add_initial_channel(apps, schema_editor):
    SystemParameter = apps.get_model('core', 'SystemParameter')
    SystemParameter.objects.create(
        parameter='channel',
        value='1',
        description='Message sending channel: 1 (Meta WhatsApp), 2 (Twilio WhatsApp), 3 (Twilio SMS)'
    )

def remove_initial_channel(apps, schema_editor):
    SystemParameter = apps.get_model('core', 'SystemParameter')
    SystemParameter.objects.filter(parameter='channel').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_channel, remove_initial_channel),
    ] 
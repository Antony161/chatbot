# Generated by Django 5.1.5 on 2025-01-25 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_rename_creared_at_chat_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='session_id',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]

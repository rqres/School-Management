# Generated by Django 4.1.2 on 2022-12-04 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='schoolterm',
            options={'ordering': ['start_date']},
        ),
        migrations.AddField(
            model_name='schoolterm',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]

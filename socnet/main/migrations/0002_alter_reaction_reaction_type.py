# Generated by Django 4.2.13 on 2024-08-24 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reaction",
            name="reaction_type",
            field=models.CharField(
                choices=[("like", "Like"), ("dislike", "Dislike")], max_length=10
            ),
        ),
    ]

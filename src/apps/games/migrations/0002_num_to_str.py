# Generated by Django 4.2.3 on 2023-07-21 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='expected_length',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='recommended_players',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]

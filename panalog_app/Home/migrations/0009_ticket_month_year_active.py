# Generated by Django 4.0.3 on 2022-06-06 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0008_alter_ticket_month_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket_month_year',
            name='Active',
            field=models.BooleanField(default=False),
        ),
    ]

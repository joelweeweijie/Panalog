# Generated by Django 4.0.3 on 2022-08-17 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0013_alter_ticket_amandays_alter_ticket_mandays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='month_year',
            field=models.ForeignKey(default='00.0000', on_delete=models.SET('00.000'), to='Home.ticket_month_year', to_field='month_year'),
        ),
    ]

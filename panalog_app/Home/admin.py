from django.contrib import admin
from .models import Ticket, Ticket_month_year, Ticket_abap_mandays
# Register your models here.

admin.site.register(Ticket)
admin.site.register(Ticket_month_year)
admin.site.register(Ticket_abap_mandays)
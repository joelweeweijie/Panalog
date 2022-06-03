from django.contrib import admin
from .models import Ticket, Ticket_month_year
# Register your models here.

admin.site.register(Ticket)
admin.site.register(Ticket_month_year)
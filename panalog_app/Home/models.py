from django.db import models
from django.urls import reverse
from users.models import User

# Create your models here.
# Mandays  models.DecimalField(null=True, blank=True, default='0', max_digits=5, decimal_places=2)
class Ticket_month_year(models.Model):
    month_year = models.CharField(max_length=30, unique=True, default='00.0000', null=True) #Jan_2022
    Active = models.BooleanField(default=False)

    def __str__(self):
        return self.month_year

#month_year = models.ForeignKey(Ticket_month_year, on_delete=models.DO_NOTHING)
class Ticket(models.Model):
    month_year = models.ForeignKey(Ticket_month_year, to_field='month_year', null=True, on_delete=models.SET_NULL)
    ticketNo = models.CharField(max_length=20) #200-238541
    type = models.CharField(null=True, blank=True, max_length=25) # change request
    team = models.CharField(null=True, blank=True, max_length=10) # BASIS
    customercode = models.CharField(null=True, blank=True, max_length=10) # PLSVN
    assigned = models.CharField(null=True, blank=True, max_length=255) # Chen, Wang
    mandays = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1, default='0.00')
    abap = models.CharField(max_length=10, default='ABAP') # ABAP
    amandays = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1, default='0.00')
    description = models.TextField(null=True, blank=True,)
    changereason = models.TextField(null=True, blank=True,)
    status = models.CharField(null=True, blank=True, max_length=20) # Active
    date_created = models.DateField(blank=True, null=True, default='1999-01-01')
    date_targetclose = models.DateField(blank=True, null=True, default='1999-01-01')
    date_close = models.DateField(blank=True, null=True, default='1999-01-01')
    requester = models.CharField(null=True, blank=True, max_length=255) # Chen, Wang
    reasoncode = models.CharField(max_length=50, null=True, blank=True) # Awaiting
    classt = models.CharField(null=True, blank=True,max_length=10, default="Inactive")
    flag = models.BooleanField(default=False)

    def __str__(self):
        return self.ticketNo

    def get_absolute_url(self):
        return reverse('ticket-detail', kwargs={'pk': self.pk})

class Ticket_abap_mandays(models.Model):
    ticketNo = models.CharField(max_length=20)  # 200-238541
    amandays = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=1, default='0.00')

    def __str__(self):
        return self.ticketNo
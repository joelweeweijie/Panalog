from django.db import models
from django.urls import reverse
from users.models import User

# Create your models here.
# Mandays  models.DecimalField(null=True, blank=True, default='0', max_digits=5, decimal_places=2)
class Ticket_month_year(models.Model):
    month_year = models.CharField(max_length=30, unique=True, default='00.0000') #Jan_2022
    Active = models.BooleanField(default=False)

    def __str__(self):
        return self.month_year

#month_year = models.ForeignKey(Ticket_month_year, on_delete=models.DO_NOTHING)
class Ticket(models.Model):
    month_year = models.ForeignKey(Ticket_month_year, to_field='month_year', on_delete=models.DO_NOTHING)
    ticketNo = models.CharField(max_length=20) #200-238541
    type = models.CharField(null=True, blank=True, max_length=25) # change request
    team = models.CharField(null=True, blank=True, max_length=10) # BASIS
    customercode = models.CharField(null=True, blank=True, max_length=10) # PLSVN
    assigned = models.CharField(null=True, blank=True, max_length=255) # Chen, Wang
    mandays = models.IntegerField(null=True, blank=True, default='0')
    abap = models.CharField(max_length=10, default='ABAP') # ABAP
    amandays = models.IntegerField(null=True, blank=True, default='0')
    description = models.TextField(null=True, blank=True,)
    changereason = models.TextField(null=True, blank=True,)
    status = models.CharField(null=True, blank=True, max_length=20) # Active
    date_created = models.DateField(null=True, blank=True)
    date_targetclose = models.DateField(null=True, blank=True)
    date_close = models.DateField(null=True, blank=True)
    requester = models.CharField(null=True, blank=True, max_length=255) # Chen, Wang
    reasoncode = models.CharField(max_length=50, null=True, blank=True) # Awaiting
    classt = models.CharField(null=True, blank=True,max_length=50) # SAP (NS)
    flag = models.BooleanField(default=False)

    def __str__(self):
        return self.ticketNo

    def get_absolute_url(self):
        return reverse('ticket-detail', kwargs={'pk': self.pk})

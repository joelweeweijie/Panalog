from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Ticket, Ticket_month_year
from users.models import Profile
import csv
import io
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import ticketform
from .decorator import member_only, manager_only
import json


# Create your views here.


def home(request):


    context = {
        'month':Ticket.objects.filter(classt="Active"),
        'title': 'Home'

    }

    return render(request, 'Home/home.html', context)

class PostListView(LoginRequiredMixin, ListView):

    model = Ticket
    template_name = 'Home/home.html'
    context_object_name = 'tix'
    def get_queryset(self):
        currentUser = (self.request.user.profile.fullname)
        return Ticket.objects.filter(classt="Active").filter(assigned=currentUser).order_by('-date_created')
    ordering = ['-date_created']
    paginate_by = 5

class UserPostListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'Home/user_ticket.html'
    context_object_name = 'tix'

    paginate_by = 4
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Ticket.objects.filter(assigned=user).order_by('-date_created')

class PostDetailView(DetailView):
    model = Ticket

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ticket
    success_url = "/flagticket/"
    def test_func(self):
        return True

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    success_url = "/"
    fields = ['mandays']

    def test_func(self):
        ticket = self.get_object()
        if (self.request.user.profile.fullname) == ticket.assigned:
            return True
        return False

@login_required
def createticket(request):
    submitted = False
    if request.method == "POST":
        form = ticketform(request.POST)
        if form.is_valid():
            q1 = form.save(commit=False)
            q1.month_year = Ticket_month_year.objects.get(month_year="00.0000")
            q1.assigned = (request.user.profile.fullname)
            q1.classt = "Active"
            q1.save()
            return HttpResponseRedirect('/create?submitted=True')
    else:
        form = ticketform
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'title': 'Create Ticket',
        'form': form,
        'submitted': submitted
    }
    return render(request, 'Home/create_ticket.html', context)

def about(request):

    context = {
        'title': 'About',
    }
    return render(request, 'Home/about.html', context)


@login_required
@manager_only
def uploadcsv(request):
    month_year_available = Ticket_month_year.objects.all()
    print("%%%%%%%%")
    print(month_year_available.values)

    testing1 = Ticket_month_year._meta.get_fields()
    print(testing1)

    context = {
        'title': 'Upload CSV',
        'month_avail': month_year_available,
    }

    if request.method == 'GET':
        return render(request, 'Home/uploadcsv.html', context)

    csv_file = request.FILES['file']
    # check if its is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Not a CSV file")
    else:
        data_set = csv_file.read().decode('UTF-8')

        month_from_model = request.POST.get("month_from_model", False)
        print(month_from_model)

        month_selected = request.POST.get("dynamic_month", False)
        year_selected = request.POST.get("dynamic_year", False)

        month_from_model = month_selected + "." + year_selected
        b = Ticket_month_year(month_year=month_from_model)
        b.save()

        io_string = io.StringIO(data_set)
        next(io_string) #skips first line in csv "header"
        for column in csv.reader(io_string, delimiter=',', quotechar='"'):
            _, created = Ticket.objects.update_or_create(
                month_year=Ticket_month_year.objects.get(month_year=month_from_model),
                ticketNo=column[0],
                type=column[1],
                team=column[2],
                customercode=column[3],
                assigned=column[4],
                #assigned=column[4] + column[5],
                mandays=column[5],
                description=column[6],
                changereason=column[7],
                status=column[8],
                date_created=column[9],
                date_targetclose=column[10],
                date_close=column[11],
                requester=column[12],
                reasoncode=column[13],
                classt=column[14]
            )
        messages.success(request, 'Successfully uploaded')
    return render(request, 'Home/uploadcsv.html', context)

@login_required
@manager_only
def export(request):

    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['ticketNo', 'type', 'team', 'customercode', 'assigned', 'mandays', 'description', 'changereason', 'status', 'date_created', 'date_targetclose', 'date_close', 'requester', 'reasoncode', 'classt'])

    for q in Ticket.objects.all().values_list('ticketNo', 'type', 'team', 'customercode', 'assigned', 'mandays', 'description', 'changereason', 'status', 'date_created', 'date_targetclose', 'date_close', 'requester', 'reasoncode', 'classt'):
        writer.writerow(q)

    response['Content-Disposition'] = 'attachment; filename="ExportedTickets.csv"'

    return response

def hallnonlogger(request):

    name_nonloggers = Ticket.objects.values("assigned").filter(classt="Active").filter(mandays="0").annotate(c1=Count("id")).order_by("-c1")

    ticket = Ticket.objects.filter(classt="Active")

    #Get the Intersection of Existing Tickets and Existing Users, as there maybe tickets made from other department, or tickets assigned to non existing users.
    tickets_zero_mandays = ticket.filter(mandays="0").values("assigned")
    qs = Profile.objects.values("fullname")
    #finding the intersection of EXISTING Users and EXISTING Tickets.
    qs1 = qs.intersection(tickets_zero_mandays)
    #retriece User_id of EXISTING Users with None logged Tickets
    qs5 = Profile.objects.filter(fullname__in=qs1).values("user_id")
    #retrieve user object based on the User_id
    total_users_who_nonlog = User.objects.filter(id__in=qs5)

    context = {
        'tix': name_nonloggers,
        'tixs': ticket,
        'title': 'NonLogger Hall',
        'trueTixnUser': total_users_who_nonlog,

    }
    return render(request, 'Home/nonlogger.html', context)

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        results = User.objects.filter(username__contains=searched)
        print(results)
    context = {
        'title': 'Search Email',
        'searched': searched,
        'result': results,
    }
    return render(request, 'Home/search_email.html', context)

@login_required
@manager_only
def month(request):

    month_year_available = Ticket_month_year.objects.all()

    active_month = Ticket.objects.filter(classt="Active")
    month_selected = ""
    year_selected = ""
    result1 = ""

    if request.method == 'POST':

        #print(var2, var3)

        #result1 = Ticket.objects.filter(date_created__year__gte=year_selected, date_created__month__gte=month_selected,date_created__year__lte=year_selected, date_created__month__lte=month_selected)
        #make all tickets currently active tickets = Inactive
        Ticket.objects.filter(classt="Active").update(classt="Inactive")
        #make tickets created in specified month Active
        #Ticket.objects.filter(date_created__year__gte=year_selected, date_created__month__gte=month_selected,date_created__year__lte=year_selected, date_created__month__lte=month_selected).update(classt="Active")

        #Ticket.objects.filter(date_close__year__gte=year_selected, date_close__month__gte=month_selected,date_close__year__lte=year_selected, date_close__month__lte=month_selected).update(classt="Active")

        month_from_drop = request.POST.get("month_from_model", False)
        print("printing the value from drop down")
        print(month_from_drop)
        q1 = Ticket.objects.filter(month_year=month_from_drop).update(classt="Active")
        print(q1)

    #new_active_month = month_selected + " " + year_selected

    context = {
        'title': 'Active Month',
        'all_ticket_created_in_month': result1,
        'active': active_month,
        'avail_months': month_year_available,
    }
    return render(request, 'Home/activemonth.html', context)


def allmember(request):
    result1 = User.objects.filter(is_staff=False)


    context = {
        'title': 'All Members',
        'result': result1,
    }
    return render(request, 'Home/allmembers.html', context)

@login_required
@manager_only
def flagtix(request):

    trueTickets = Ticket.objects.all().filter(classt="Active").values("assigned")
    trueUsers = Profile.objects.values("fullname")
    #trueUsers2 = User.objects.all().values("first_name", "last_name")
    #print(trueTickets)
    #print(trueUsers)
    qs2 = trueTickets.difference(trueUsers)
    #print("Abnormal User Found")
    #print(qs2)

    qs = Ticket.objects.filter(assigned__in=qs2)
    qs.update(flag=True)


    #print("Users")
    #print(qs)

#ertyjk
    context = {
        'title': 'Flag Ticket',
        'flagticket': qs,
    }
    return render(request, 'Home/flagtix.html', context)
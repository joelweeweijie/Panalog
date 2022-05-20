from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Ticket
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
        assigned = (self.request.user.last_name + ", " + self.request.user.first_name)
        print(assigned)
        return Ticket.objects.filter(classt="Active").filter(assigned=assigned).order_by('-date_created')
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
    success_url = "/"
    def test_func(self):
        return True

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    success_url = "/"
    fields = ['mandays']

    def test_func(self):
        ticket = self.get_object()
        if (self.request.user.last_name + ", " + self.request.user.first_name) == ticket.assigned:
            return True
        return False

def createticket(request):
    submitted = False
    if request.method == "POST":
        form = ticketform(request.POST)
        if form.is_valid():
            q1 = form.save(commit=False)
            q1.assigned = (request.user.last_name + ", " + request.user.first_name)
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
    context = {
        'tix':Ticket.objects.all(),
        'title': 'Upload CSV'
    }
    if request.method == 'GET':
        return render(request, 'Home/uploadcsv.html', context)

    csv_file = request.FILES['file']
    # check if its is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Not a CSV file")
    else:
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) #skips first line in csv "header"
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = Ticket.objects.update_or_create(
                ticketNo=column[0],
                assigned=column[1],
                description=column[2],
                date_created=column[3] #YYYY-MM-DD
            )

        messages.success(request, 'Successfully uploaded')
    return render(request, 'Home/uploadcsv.html', context)

@login_required
@manager_only
def export(request):

    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['ticketNo', 'assigned', 'description', 'date_created'])

    for q in Ticket.objects.all().values_list('ticketNo', 'assigned', 'description', 'date_created'):
        writer.writerow(q)

    response['Content-Disposition'] = 'attachment; filename="ExportedTickets.csv"'

    return response

def hallnonlogger(request):

    nonlog = Ticket.objects.values("assigned").filter(classt="Active").filter(mandays="0").annotate(c1=Count("id")).order_by("-c1")

    ticket = Ticket.objects.filter(classt="Active")

    #Get the Intersection of Existing Tickets and Existing Users, as there maybe tickets made from other department, or tickets assigned to non existing users.
    trueTickets = ticket.filter(mandays="0").values("assigned")
    print("True Tickets")
    print(trueTickets)
    #trueUsers = User.objects.all().values("username")
    #trueUsers = User.object.values("fullname")
    #print("True Users")
    #print(trueUsers)
    qs = Profile.objects.values("fullname")

    print(qs)
    qs6 = Profile.objects.values("user_id", "fullname")
    print("USERID ")
    print(qs6)



    qs1 = qs.intersection(trueTickets)
    print("INTERSECTION HERE")
    print(qs1)
    #print(qs1)
    #print("GGGGGGGGGGGGGGGG")
    #print(qs1)
    qs5 = Profile.objects.filter(fullname__in=qs1).values("user_id")
    print("GET the ID of the USER using profile.fullname")
    print(qs5)
    #qs = User.objects.filter(username__in=["Jack","Joel"])
    qs3 = User.objects.filter(id__in=qs5)
    print("Getting User.object where ID is IN ")
    print(qs3)
    #print("Users")
    #print(qs)
    #print(qs)


    context = {
        'tix': nonlog,
        'tixs': ticket,
        'title': 'NonLogger Hall',
        'trueTixnUser': qs3,

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
    tixs = Ticket.objects.filter(classt="Active")
    var2 = ""
    var3 = ""
    result1 = ""

    if request.method == 'POST':
        var2 = request.POST.get("letter", False)
        var3 = request.POST.get("year", False)
        print(var2, var3)

        result1 = Ticket.objects.filter(date_created__year__gte=var3, date_created__month__gte=var2,
                                     date_created__year__lte=var3, date_created__month__lte=var2)

        Ticket.objects.filter(classt="Active").update(classt="Inactive")

        Ticket.objects.filter(date_created__year__gte=var3, date_created__month__gte=var2,
                              date_created__year__lte=var3, date_created__month__lte=var2).update(classt="Active")

    active = var2 + " " + var3

    context = {
        'title': 'Active Month',
        'result': result1,
        'active': active,
        'tixs': tixs,

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

    print(trueTickets)
    print(trueUsers)
    qs2 = trueTickets.difference(trueUsers)
    print("Abnormal User Found")
    print(qs2)

    qs = Ticket.objects.filter(assigned__in=qs2)
    print("Users")
    print(qs)



    context = {
        'title': 'Flag Ticket',
        'flagticket': qs,
    }
    return render(request, 'Home/flagtix.html', context)
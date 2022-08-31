import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Ticket, Ticket_month_year, Ticket_abap_mandays
from users.models import Profile
import csv
import io, datetime
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import ticketform
from .decorator import member_only, manager_only
import json
import pandas as pd

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
    context_object_name = 'userstickets'
    def get_queryset(self):
        currentUser = (self.request.user.profile.fullname)
        return Ticket.objects.filter(classt="Active").filter(assigned=currentUser).order_by('-date_created')
    ordering = ['-date_created']
    paginate_by = 5
    extra_context = {'activemnth': Ticket_month_year.objects.filter(Active=True)}

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

    currentactivemonth = Ticket_month_year.objects.get(Active=True)

    submitted = False
    if request.method == "POST":
        form = ticketform(request.POST)
        if form.is_valid():
            q1 = form.save(commit=False)
            q1.month_year = Ticket_month_year.objects.get(month_year=currentactivemonth)
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

    context = {
        'title': 'Upload CSV',
        'month_avail': month_year_available,
    }

    if request.method == 'GET':
        return render(request, 'Home/uploadcsv.html', context)
    try:
        month_from_model1 = request.POST.get("month_from_model", False)
        # print("Month_from_model")
        # print(month_from_model1)

        month_selected = request.POST.get("dynamic_month", False)
        year_selected = request.POST.get("dynamic_year", False)

        month_from_model = month_selected + "." + year_selected
        # print("month_selected + year_selected")
        # print(month_from_model)

        b = Ticket_month_year(month_year=month_from_model)
        b.save()

    except Exception as e:
        messages.error(request, "Release Date Error " + repr(e))

    try:
        csv_file = request.FILES['file']
        # check if its is a csv file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Not a CSV file")
        else:
            data_set = csv_file.read().decode('UTF-8')
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
            io_string.close()
    except Exception as e:
        messages.error(request, "Unable to Upload " + repr(e))

    return render(request, 'Home/uploadcsv.html', context)

@login_required
@manager_only
def uploadrawcsv(request):

    #decalre template
    template = "Home/uploadrawcsv.html"
    month_avail = Ticket_month_year.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be ####',
        'month_avail': month_avail
    }

    if request.POST.get('delete'):
        selected = request.POST.get("month_from_model")
        print("$$$$$$$$$$$$$$$")
        print(selected)

        Ticket.objects.filter(month_year=selected).delete()
        Ticket_month_year.objects.filter(month_year=selected).delete()

        #q2 = Ticket_month_year.objects.filter(id__in=request.POST.get())
        #q1 = Ticket.objects.filter(month_year=selected)
        #q1.delete()

    context = {
        'month_avail': month_avail
    }

    return render(request, template, context)

@login_required
@manager_only
def pandasupload(request):

    context = {
        'title': 'PandasUpload',
    }

    if request.method == "GET":
        return render(request, 'Home/uploadpandas.html', context)

    try:
        isabapcsv = request.POST.get("abap_selected")
        # print("Month_from_model")
        # print(month_from_model1)
        print(isabapcsv)


        csv_file = request.FILES['file']

        df = pd.read_csv(csv_file, sep=',')
        if isabapcsv == "No":

            month_selected = request.POST.get("dynamic_month", False)
            year_selected = request.POST.get("dynamic_year", False)

            month_from_model = month_selected + "." + year_selected
            # print("month_selected + year_selected")
            # print(month_from_model)

            b = Ticket_month_year(month_year=month_from_model)
            b.save()

            print("Entered isabapvsb = No")
            df['Created Date'] = df['Created Date'].fillna('1999-01-01')
            df['SLA Target Date'] = df['SLA Target Date'].fillna('1999-01-01')
            row_iter = df.iterrows()

            objs = [
                Ticket(
                    month_year=Ticket_month_year.objects.get(month_year=month_from_model),
                    ticketNo=row[28],
                    type=row[20],
                    customercode=row[10],
                    assigned=row[19],
                    description=row[39],
                    changereason=row[40],
                    status=row[21],
                    date_created=row[29],
                    date_targetclose=row[31],
                    # date_close=row[33],
                    requester=row[9],
                    reasoncode=row[24],
                )
                for index, row in row_iter
            ]
            Ticket.objects.bulk_create(objs)
            messages.success(request, 'Successfully uploaded CSV')
        elif isabapcsv == "Yes":
            print("Entered isabapvsb = Yes")
            row_iter = df.iterrows()
            objs = [
                Ticket(
                    ticketNo=row[0],
                    amandays=row[6],
                )
                for index, row in row_iter
            ]
            Ticket_abap_mandays.objects.bulk_create(objs)
            messages.success(request, 'Successfully uploaded ABAP CSV')
    except Exception as e:
        messages.error(request, "Error Name Exists! :" + repr(e))



    return render(request, 'Home/uploadpandas.html', context)

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

    active_month = Ticket_month_year.objects.filter(Active=True)
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
        'tixs': active_month,
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

    month_year_available = Ticket_month_year.objects.all().order_by('-id')
    active_month = Ticket.objects.filter(classt="Active")
    active_month1 = Ticket_month_year.objects.filter(Active=True)
    print(active_month1.values)
    month_selected = ""
    year_selected = ""

    if request.method == 'POST':

        month_from_drop = request.POST.get("month_from_model", False)
        #print("printing the value from drop down")
        #print(month_from_drop)
        Ticket_month_year.objects.filter(Active=True).update(Active=False)
        setActive = Ticket_month_year.objects.filter(month_year=month_from_drop).update(Active=True)
        #print(setActive)
        # make all tickets currently active tickets = Inactive
        Ticket.objects.filter(classt="Active").update(classt="Inactive")
        q1 = Ticket.objects.filter(month_year=month_from_drop).update(classt="Active")
        #print(q1)

    #new_active_month = month_selected + " " + year_selected

    context = {
        'title': 'Active Month',
        'active': active_month,
        'active1': active_month1,
        'avail_months': month_year_available,
    }
    return render(request, 'Home/activemonth.html', context)


def allmember(request):
    getmembers = User.objects.filter(is_staff=False)


    context = {
        'title': 'All Members',
        'result': getmembers,
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

    if request.POST.get('delete'):
        q1 = Ticket.objects.filter(id__in=request.POST.getlist('ticketitem'))
        q1.delete()


    #FINDING DUPLICATE TICKETS BASED ON THE "ticketNo"
    #dupes = Ticket.objects.values('ticketNo').annotate(Count('id')).order_by().filter(id__count__gt=1)

    #result1 = Ticket.objects.filter(ticketNo__in=[item['ticketNo'] for item in dupes])

    #print(result1)



    context = {
        'title': 'Flag Ticket',
        'flagticket': qs,
    }
    return render(request, 'Home/flagtix.html', context)

@login_required
@manager_only
def combine(request):
    month_year_available = Ticket_month_year.objects.all().order_by('-id')

    if request.method == "POST":
        final_naming = request.POST.get("combined_name")
        month_open = request.POST.get("open")
        month_create = request.POST.get("create")
        month_close = request.POST.get("close")

        #print(final_naming)
        #print(month_open)
        #print(month_create)
        #print(month_close)

        b = Ticket_month_year(month_year=final_naming)
        b.save()

        #field_names = Ticket._meta.get_fields()
        #print(field_names)
        openTicket = Ticket.objects.filter(month_year=month_open)
        #print(openTicket)
        #print("=======================")
        createTicket = Ticket.objects.filter(month_year=month_create)
        #print(createTicket)
        #print("=======================")
        closeTicket = Ticket.objects.filter(month_year=month_close)
        #print(closeTicket)
        #print("=======================")

        OpennClose = openTicket | createTicket
        combined = OpennClose | closeTicket

        df1 = pd.DataFrame(Ticket.objects.filter(month_year=month_open).values())
        df2 = pd.DataFrame(Ticket.objects.filter(month_year=month_create).values())
        df3 = pd.DataFrame(Ticket.objects.filter(month_year=month_close).values())
        print("After setting df1, df2, df3")
        #print(df1.columns)

        print("@@@@@@@@@@@@@@@@@@@@ OPEN")
        print(df1)
        print("@@@@@@@@@@@@@@@@@@@@ CREATE")
        print(df2)
        print("@@@@@@@@@@@@@@@@@@@@ CLOSE")
        print(df3)
        print("%%%%%%%%%%%%%%%%%%%% MERGE FOR DF1, DF2")

        df1df2 = pd.concat([df1, df2]).drop_duplicates('ticketNo')

        dup1 = pd.merge(df1, df2, how="right", on=["ticketNo"])
        print(dup1)
        print("******************** DF3 included")

        dup2 = pd.merge(df1df2, df3, how="right", on=["ticketNo"])
        print(dup2)
        print("++++++++++++++FINALRESULTS+++++++++++")

        dup3 = pd.concat([dup1, dup2])
        dup4 = dup3 ['id_x'].dropna().astype(int).tolist()
        print(dup4)
        #DELETE THE DUPLICATE TICKETS
        query1 = Ticket.objects.filter(id__in=dup4)
        print(query1)
        query1.delete()
        #COMBINE THE 3 Files and SAVE/UPDATE
        combined.update(month_year=final_naming)



    context = {
        'title': 'CombineCSV',
        'avaiable_months': month_year_available,

    }

    return render(request, 'Home/manage.html', context)
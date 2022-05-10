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
        return Ticket.objects.filter(classt="Active").filter(assigned=self.request.user.first_name).order_by('-date_created')
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
        ticket = self.get_object()
        if self.request.user.username == ticket.assigned:
            return True
        return False

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    success_url = "/"
    fields = ['mandays']

    def test_func(self):
        ticket = self.get_object()
        if self.request.user.username == ticket.assigned:
            return True
        return False

def createticket(request):
    submitted = False
    if request.method == "POST":
        form = ticketform(request.POST)
        if form.is_valid():
            q1 = form.save(commit=False)
            q1.assigned = request.user.username
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
    #user = User.objects.get(id=4)
    #print("USER", user.__dict__)

    #print(request.user.get_full_name())

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

    response['Content-Disposition'] = 'attachment; filename="questions.csv"'

    return response

def hallnonlogger(request):

    nonlog = Ticket.objects.values("assigned").filter(classt="Active").filter(mandays="0").annotate(c1=Count("id")).order_by("-c1")
    #print(nonlog)
    #print("index 0: ",nonlog[0])

    #mydata = Ticket.objects.filter(mandays="0").values("assigned").annotate(Count('id', distinct=True))
    mydata = Ticket.objects.all().filter(classt="Active").filter(mandays="0").values("assigned")
    #print("Printing 0 Manday ticket people", mydata)

    #to_find = "Joel"

    #for s in range(len(nonlog)):
    #    if nonlog[s]["assigned"] == to_find:
    #        print("{} no. of nonlog  is {} from module.".format(nonlog[s]["assigned"], nonlog[s]["c1"]))
    #        print()
    #print("+++++++++++++++++++++")
    non = Profile.objects.all()

    t1 = User.objects.all().values("username")
    #print("Printing User Object ", t1)
    #print("#################################")
    #Get Registered Users and Intersection with Active Tickets to show (Registered & has Tickets)
    #Tickets will have users who are not in PANALOG aka. randomly made tickets but assigned in AP
    qs1 = t1.intersection(mydata)

    qs1_list = list(qs1)
    print("GGGGGGGGGGGGGGGG")
    print(qs1)
    string = ",".join([item['username'] for item in qs1_list])
    #print("======Names of People who Registered and have Tickets=======")
    #print(string)
    result1 = ""
    s = []
    for i in range(len(qs1_list)):
        s.append(qs1_list[i]['username'])
    result1 = '","'.join(s)
    result1 = '"' + result1 + '"'
    print("+++++++++++++++++")
    print("result1 = "+result1)


    qs2_list = ''.join([str(x) for x in qs1_list])

    #print(''.join([str(x) for x in qs1_list]))
    #print("JJJJJJJJJJJJJJJJJJJ")
    #print(qs2_list)
    #print(" ".join(qs1_list))
    my_string = qs2_list
    remove = ['username']
    for value in remove:
        my_string = my_string.replace(value, '')
    #print(my_string)

    punctuation = '''!/?@#$%^&*_~()-[]{};:'"\,<>.'''
    my_string2 = my_string
    remove_punct = ""
    for character in my_string2:
        if character not in punctuation:
            remove_punct = remove_punct + character
    #print(remove_punct)

    #for nonloger in non:
    #    print(nonloger.user.email)

    #for i in qs1_list
     #   list

    #output = User.objects.filter(username__in=["Jack","Joel"])
    #filter_dict = {'username__in':["Jack","Joel"]}
    #output = User.objects.filter(**{username: result1})
    #qs = User.objects.filter(**{search_field: result1})
    qs = User.objects.filter(username__in=["Jack","Joel"])
    #output = User.objects.filter(username__in=[result1])
    #print(output)
    print(qs)


    context = {
        'tix': nonlog,
        'title': 'hall',
        'email': non,
        'ticketandmember' : qs1,
        'test': qs,

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

    }
    return render(request, 'Home/activemonth.html', context)


def allmember(request):
    result1 = User.objects.filter(is_staff=False)
    context = {
        'title': 'All Members',
        'result': result1,
    }
    return render(request, 'Home/allmembers.html', context)


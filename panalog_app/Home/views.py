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


# Create your views here.


def home(request):
    context = {
        'tix':Ticket.objects.all(),
        'title': 'Home'

    }

    return render(request, 'Home/home.html', context)

class PostListView(ListView):

    model = Ticket
    template_name = 'Home/home.html'
    context_object_name = 'tix'
    def get_queryset(self):
        return Ticket.objects.filter(assigned=self.request.user).order_by('-date_created')
    #oder tickets based on date created "-" means newest first
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

    user = User.objects.get(id=4)
    print("USER", user.__dict__)

    context = {
        'title': 'About',
    }
    return render(request, 'Home/about.html', context)

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

def export(request):
    #this will export the current Entire Ticket table into a csv
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['ticketNo', 'assigned', 'description', 'date_created'])

    for q in Ticket.objects.all().values_list('ticketNo', 'assigned', 'description', 'date_created'):
        writer.writerow(q)

    response['Content-Disposition'] = 'attachment; filename="questions.csv"'

    return response

def hallnonlogger(request):

    nonlog = Ticket.objects.values("assigned").filter(mandays="0").annotate(c1=Count("id")).order_by("-c1")
    #print(nonlog)
    #print("index 0: ",nonlog[0])

    #mydata = Ticket.objects.filter(mandays="0").values("assigned").annotate(Count('id', distinct=True))
    mydata = Ticket.objects.all().filter(mandays="0").values("assigned")
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
    qs1 = t1.intersection(mydata)
    qs1_list = list(qs1)
    print("GGGGGGGGGGGGGGGG")
    print(qs1_list)
    print("HHHHHHHHHHHHHH")
    qs2_list = ''.join([str(x) for x in qs1_list])
    print(''.join([str(x) for x in qs1_list]))
    print("JJJJJJJJJJJJJJJJJJJ")

    #print(" ".join(qs1_list))
    my_string = qs2_list
    remove = ['username']
    for value in remove:
        my_string = my_string.replace(value, '')
    print(my_string)

    punctuation = '''!/?@#$%^&*_~()-[]{};:'"\,<>.'''
    my_string2 = my_string
    remove_punct = ""
    for character in my_string2:
        if character not in punctuation:
            remove_punct = remove_punct + character
    print(remove_punct)

    #for nonloger in non:
    #    print(nonloger.user.email)

    #for i in qs1_list
     #   list


    context = {
        'tix': nonlog,
        'title': 'hall',
        'email': non,
        'ticketandmember' : qs1

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

def team(request):
    user1 = User.objects.filter(is_staff=False)

    context = {
        'title': 'Module Team',
        'user': user1,
    }
    return render(request, 'Home/team.html', context)

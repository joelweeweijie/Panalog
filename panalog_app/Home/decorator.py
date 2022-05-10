from django.shortcuts import redirect

def manager_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'member':
            return redirect('Pana-home')
        if group == 'manager':
            return view_func(request, *args, **kwargs)

    return wrapper_function


def member_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'manager':
            return redirect('Pana-home')
        if group == 'member':
            return view_func(request, *args, **kwargs)

    return wrapper_function
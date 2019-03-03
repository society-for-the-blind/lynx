from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import generic

from .models import Contact
from .forms import IntakeForm


def index(request):
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return render(request, 'lynx/index.html', context)


def client_list(request):
    template = loader.get_template('lynx/clients.html')
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return HttpResponse(template.render(context, request))


def add_intake(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/index/')

    else:
        form = IntakeForm()

    return render(request, 'lynx/new_intake.html', {'form': form})

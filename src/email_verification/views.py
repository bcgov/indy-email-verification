from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({"test": 123}, request))
    # return render(request, "index.html", )

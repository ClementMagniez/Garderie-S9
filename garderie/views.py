from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Child
from django.urls import reverse
from django.views import generic

class ListChildrenView(generic.ListView):
        template_name='garderie/index.html'
        context_object_name='children_list'
        
        def get_queryset(self):
                return Child.objects.all()
                


class DetailView(generic.DetailView):
        model=Child
        template_name='garderie/detail.html'


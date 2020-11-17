from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Child
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User

class ListChildrenView(generic.ListView):
	template_name='garderie/index.html'
	context_object_name='children_list'

	def get_queryset(self):
		return Child.objects.all()

#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		context['user'] = User
#		return context
#                

class DetailView(generic.DetailView):
	model=Child
	template_name='garderie/detail.html'


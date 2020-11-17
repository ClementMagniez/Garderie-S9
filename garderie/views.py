from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Child, Parent
from django.urls import reverse
from django.views import generic

class IndexRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		user=self.request.user
		if user.is_superuser:
			return reverse('admin_view')
#		elif user.is_staff:
#			return reverse('educ_view')
#		else:
#			return reverse('parent_view')

class AdminIndexView(generic.ListView):
	template_name="garderie/admin-index.html"
	context_object_name='parent_list'

	def get_queryset(self):
		return Parent.objects.all()


class ListChildrenView(generic.ListView):
	template_name='garderie/index.html'
	context_object_name='children_list'

	def get_queryset(self):
		return Child.objects.all()


class ChildProfileView(generic.DetailView):
	model=Child
	template_name='garderie/child_profile.html'

class ParentProfileView(generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'



#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		context['child'] = Child.objects.all()
#		return context


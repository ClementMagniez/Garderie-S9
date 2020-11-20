from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import Child, Parent
from .forms import NewUserForm
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
	template_name="garderie/admin_index.html"
	context_object_name='parent_list'

	def get_queryset(self): 
		return Parent.objects.all()



class ParentListView(generic.ListView):
	template_name="garderie/parent_list.html"
	context_object_name='parent_list'

	def get_queryset(self):
		return Parent.objects.all()


class ChildListView(generic.ListView):
	template_name='garderie/children_list.html'
	context_object_name='children_list'

	def get_queryset(self):
		return Child.objects.all()


class ChildProfileView(generic.DetailView):
	model=Child
	template_name='garderie/child_profile.html'

class ParentProfileView(generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'


# Essayer : utiliser FormView et tout save à la main

class NewUserView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_user.html'
	form_class = NewUserForm
	success_url = '/parent/'

	# Crée le parent ET l'utilisateur lié au parent par leur id commun 
	def form_valid(self, form):
#		self.object=form.save(commit=False)


		return super().form_valid(form)


#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		context['child'] = Child.objects.all()
#		return context


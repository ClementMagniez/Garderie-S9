from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Child, Parent, Config
from django.urls import reverse, reverse_lazy
from django.views import generic
from .forms import *

class IndexRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		user=self.request.user
		if user.is_superuser:
			return reverse('admin_index')
		elif user.is_staff:
			return reverse('educ_index')
		else:
			return reverse('parent_index')

class EducRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		return reverse('children_list')

class ParentRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		user=self.request.user
		return reverse('parent_profile', args=[user.id])		


class AdminIndexView(generic.TemplateView):
	template_name="garderie/admin_index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['hourlyrate'] = Config.objects.get(pk="hourlyrate")
		return context




class ChildrenListView(generic.ListView):
	template_name='garderie/children_list.html'
	context_object_name='children_list'

	def get_queryset(self):
		return Child.objects.all()


class ParentListView(generic.ListView):
	template_name="garderie/parent_list.html"
	context_object_name='parent_list'

	def get_queryset(self):
		return Parent.objects.all()


class ChildProfileView(generic.DetailView):
	model=Child
	template_name='garderie/child_profile.html'

class ParentProfileView(generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'


class NewUserView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_user.html'
	form_class = NewUserForm
	success_url = '/parent/'
	


class NewChildView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_child.html'
	form_class = NewChildForm
	success_url = reverse_lazy('children_list') # TODO plutôt renvoyer sur le profil ?
	

class ParentDeleteView(generic.edit.DeleteView):
	template_name='garderie/parent_profile.html'
	model = Parent
	success_url = reverse_lazy('parent_list')

	def delete(self, request, *args, **kwargs):
		self.object=self.get_object()
		User.objects.filter(id=self.object.uid_id).delete()
		self.object.delete()
		return HttpResponseRedirect(self.success_url)

class ChildDeleteView(generic.edit.DeleteView):
	template_name='garderie/child_profile.html'
	model = Child
	success_url = reverse_lazy('children_list')

class HourlyRateEditView(generic.edit.UpdateView): # TODO voir si le nom est cohérent (selon la table Config)
	template_name='garderie/forms/edit_rate_form.html'
	model = Config 
	fields=['value']
	success_url = reverse_lazy('admin_index') # '/admin/accueil/'



#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		context['child'] = Child.objects.all()
#		return context


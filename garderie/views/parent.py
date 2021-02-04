from django.views import generic
from ..models import User, Child, Parent, ReliablePerson
from ..forms import ParentUpdateForm, NewReliableForm, NewChildFormParent
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..utils import is_parent_permitted, EmbeddedCreateView, EmbeddedUpdateView

# Contient les views concernant les parents 


# Profil d'un parent donné
class ParentProfileView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'

	def test_func(self):
		return is_parent_permitted(self)
		
	# Transmet la requête actuelle aux views récupérant le POST de deux formulaires :
	# new_child_form crée un NewChildFormParent et passe la requête à ParentCreateChildView
	# personal_data_form crée un ParentUpdateForm et passe la requête à EditUserByUserView
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['new_child_form'] = NewChildFormParent(pk=self.kwargs['pk'])
		context['new_child_action'] =reverse('parent_create_child', kwargs={'pk':self.kwargs['pk']})
		context['new_reliable_form'] = NewReliableForm(pk=self.kwargs['pk'])
		context['new_reliable_action']=reverse('parent_create_reliable', kwargs={'pk':self.kwargs['pk']})
		context['personal_data_form'] = ParentUpdateForm(pk=self.kwargs['pk'],instance=User.objects.get(pk=self.kwargs['pk']),
																										 initial={'phone':self.object.phone})
		context['personal_data_action']=reverse('parent_update', kwargs={'pk':self.kwargs['pk']})
		today=timezone.now()
		context['bills']=self.object.bill_set.all()
		return context
	
# TODO validation et EmbeddedForm 	
# Formulaire d'édition d'un parent donné, embedded dans ParentProfileView
class ParentUpdateView(LoginRequiredMixin, UserPassesTestMixin, EmbeddedUpdateView):
	form_class=ParentUpdateForm
	model = User
	
	def test_func(self):
		return is_parent_permitted(self)
		
	def get_success_url(self):
		return reverse('parent_profile', args=[self.kwargs['pk']])

# Formulaire de création d'une personne de confiance (susceptible d'être récupérée par le parent)
class CreateReliableView(LoginRequiredMixin, UserPassesTestMixin, EmbeddedCreateView):
	form_class=NewReliableForm
	
	def test_func(self):
		return is_parent_permitted(self)
		
	def get_success_url(self):
		return reverse('parent_profile', args=[self.kwargs['pk']])

# Formulaire de création d'un enfant par le parent
class ParentCreateChildView(LoginRequiredMixin, UserPassesTestMixin, EmbeddedCreateView):
	form_class=NewChildFormParent
	
	def test_func(self):
		return is_parent_permitted(self)
		
	def get_success_url(self):
		return reverse('parent_profile', args=[self.kwargs['pk']])
			

# Formulaire de suppression d'une personne de confiance
class ParentDeleteReliableView(generic.edit.DeleteView):
	model = ReliablePerson
	
	def get_success_url(self):
		return self.request.GET.get('next') # évite un changement de page

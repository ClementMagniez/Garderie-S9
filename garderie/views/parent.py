from django.views import generic
from ..models import Child, Parent, ReliablePerson
from ..forms import ParentUpdateForm, NewReliableForm, NewChildFormParent
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..utils import is_parent_permitted, EmbeddedCreateView

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
		context['personal_data_form'] = ParentUpdateForm(instance=User.objects.get(pk=self.kwargs['pk']),
																										 initial={'phone':self.object.phone})
		return context
	
# TODO validation et EmbeddedForm 	
# Formulaire d'édition d'un parent donné, embedded dans ParentProfileView
class ParentUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView):
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
			

# Formulaire de suppression d'un parent (et de l'utilisateur associé)
class ParentDeleteView(generic.edit.DeleteView):
	template_name='garderie/parent_profile.html'
	model = Parent
	success_url = reverse_lazy('parent_list')

	def delete(self, request, *args, **kwargs):
		self.object=self.get_object()
		User.objects.filter(id=self.object.uid_id).delete()
		self.object.delete()
		return HttpResponseRedirect(self.success_url)

# Formulaire de suppression d'une personne de confiance
class ParentDeleteReliableView(generic.edit.DeleteView):
	model = ReliablePerson
	
	def get_success_url(self):
		return self.request.GET.get('next') # évite un changement de page

from django.views import generic
from ..models import Child, Parent, ReliablePerson
from ..forms import ParentUpdateForm, NewReliableForm, NewChildFormParent, NewUserForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

# Contient les views concernant les parents 


# Liste des parents, fournit au HTML tous les Parent
class ParentListView(generic.ListView):
	template_name="garderie/parent_list.html"
	context_object_name='parent_list'

	def get_queryset(self):
		return Parent.objects.all()

# Profil d'un parent donné
class ParentProfileView(generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'

	# Transmet la requête actuelle aux views récupérant le POST de deux formulaires :
	# new_child_form crée un NewChildFormParent et passe la requête à ParentCreateChildView
	# personal_data_form crée un ParentUpdateForm et passe la requête à EditUserByUserView
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['new_child_form'] = NewChildFormParent(request=self.request)
		context['new_reliable_form'] = NewReliableForm(request=self.request)
		context['personal_data_form'] = ParentUpdateForm(request=self.request,
																										 instance=self.object.uid,
																										 initial={'phone':self.object.phone})
		return context
	
# Formulaire d'édition d'un parent donné, embedded dans ParentProfileView
class ParentUpdateView(generic.edit.UpdateView):
	form_class=ParentUpdateForm
	model = User
	
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['request']=self.request
		return kwargs
		
	def get_success_url(self):
		return reverse('parent_profile', args=[self.request.user.id])

# Formulaire de création d'une personne de confiance (susceptible d'être récupérée par le parent)
class CreateReliableView(generic.edit.CreateView):
	form_class=NewReliableForm
	
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['request']=self.request
		return kwargs
			
	def get_success_url(self):
		return reverse('parent_profile', args=[self.kwargs['pk']])

# Formulaire de création d'un enfant par le parent
class ParentCreateChildView(generic.edit.CreateView):
	form_class=NewChildFormParent
	
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['request']=self.request
		return kwargs
			
	def get_success_url(self):
		return reverse('parent_profile', args=[self.request.user.id])
	

# Formulaire de création d'un nouveau parent
class NewUserView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_user.html'
	form_class = NewUserForm
	success_url = '/parent/'
	
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
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page




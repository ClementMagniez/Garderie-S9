from django.views import generic
from ..models import Child, Schedule, Parent, ExpectedPresence
from ..forms import NewPresenceForm, ChildUpdateForm, NewChildFormAdmin, EditScheduleForm
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from ..utils import EmbeddedCreateView, EmbeddedUpdateView

# Contient toutes les views manipulant principalement les Children



# Liste des enfants, fournit tous les Child ainsi que chaque Schedule encore
# incomplet (départ indéterminé) et un Schedule proche (arrivée +- une heure)
class ChildrenListView(generic.ListView):
	template_name='garderie/children_list.html'
	context_object_name='children_list'

	# all_children : tous les Children de la DB
	# current_schedules : tous les Schedules incomplets (selon ScheduleManager#incomplete_schedules)
	def get_queryset(self):

		return {'all_children': Child.objects.all(), 
						'current_schedules': Schedule.objects.incomplete_schedules()
					 }

# Profil d'un enfant donné
class ChildProfileView(generic.DetailView):
	model=Child
	template_name='garderie/child_profile.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['schedule_form'] = NewPresenceForm(pk=self.kwargs['pk'])
		context['action']=reverse('schedule_register', kwargs={'pk':self.kwargs['pk']}) # même URL donc sûrement améliorable
		context['personal_data_form'] = ChildUpdateForm(instance=self.object)	
		return context
	
	
class EditScheduleView(EmbeddedUpdateView):
	model=Schedule	
	form_class=EditScheduleForm		
	
	def get_success_url(self):
		return reverse('child_profile', args=[self.kwargs['pk']])
	
# Formulaire de création d'un schedule
class CreatePresenceView(EmbeddedCreateView):
	form_class=NewPresenceForm
	
	def get_success_url(self):
		print("lol")
		return reverse('child_profile', args=[self.kwargs['pk']])
	
# Formulaire d'édition d'un enfant donné, embedded dans ChildProfileView
class ChildUpdateView(generic.edit.UpdateView):
	form_class=ChildUpdateForm
	model = Child
	
	def get_success_url(self):
		print("test")
		return reverse('child_profile', args=[self.kwargs['pk']])
	

# Formulaire de création d'un nouvel enfant par l'admin
class NewChildView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_child.html'
	form_class = NewChildFormAdmin
	success_url = reverse_lazy('children_list') # TODO plutôt renvoyer sur le profil ?


# Formulaire de suppression d'une ExpectedPresence
class PresenceDeleteView(generic.edit.DeleteView):
	model = ExpectedPresence
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page

# Formulaire de suppression d'un Schedule
class ScheduleDeleteView(generic.edit.DeleteView):
	model = Schedule
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page



# Formulaire de suppression d'un enfant
class ChildDeleteView(generic.edit.DeleteView):
	template_name='garderie/child_profile.html'
	model = Child
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page


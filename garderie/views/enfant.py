from django.views import generic
from ..models import Child, Schedule, Parent
from ..forms import NewScheduleForm, ChildUpdateForm, NewChildFormAdmin
from django.urls import reverse, reverse_lazy

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
		context['schedule_form'] = NewScheduleForm(pk=self.kwargs['pk'])
		context['action']=reverse('schedule_register', kwargs={'pk':self.kwargs['pk']}) # même URL donc sûrement améliorable
		context['personal_data_form'] = ChildUpdateForm(instance=self.object)	
		return context
	
# Formulaire de création d'un schedule
class CreateScheduleView(generic.edit.CreateView):
	form_class=NewScheduleForm
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['pk']=self.kwargs['pk']
		return kwargs
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['action']=reverse('schedule_register', kwargs={'pk':self.kwargs['pk']}) # même URL donc sûrement améliorable
		return context
			
	def get_success_url(self):
		return reverse('child_profile', args=[self.kwargs['pk']])
	
# Formulaire d'édition d'un enfant donné, embedded dans ChildProfileView
class ChildUpdateView(generic.edit.UpdateView):
	form_class=ChildUpdateForm
	model = Child
	
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		return kwargs
		
	def get_success_url(self):
		return reverse('child_profile', kwargs={'pk':self.kwargs['pk']})


# Formulaire de création d'un nouvel enfant par l'admin
class NewChildView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_child.html'
	form_class = NewChildFormAdmin
	success_url = reverse_lazy('children_list') # TODO plutôt renvoyer sur le profil ?


# Formulaire de suppression d'un schedule
class ScheduleDeleteView(generic.edit.DeleteView):
#	template_name='garderie/child_garde	profile.html'
	model = Schedule
	
#	def delete(self, request, *args, **kwargs):
#		self.object=self.get_object()
#		self.success_url=self.get_success_url()
#		self.object.delete()
#		self.object.update_bill()
#		return HttpResponseRedirect(success_url)
		
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page


# Formulaire de suppression d'un enfant
class ChildDeleteView(generic.edit.DeleteView):
	template_name='garderie/child_profile.html'
	model = Child
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page


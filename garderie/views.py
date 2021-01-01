from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Child, Parent, HourlyRate, Schedule
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from .forms import *

# Redirection après le login selon le type d'utilisateur
class IndexRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		user=self.request.user
		if user.is_superuser:
			return reverse('admin_index')
		elif user.is_staff:
			return reverse('educ_index')
		else:
			return reverse('parent_index')

# TODO Voir s'il ne serait pas tout aussi simple de 
# se débarrasser de EducRedirect et ParentRedirect

# Redirection d'une éducatrice
class EducRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		return reverse('children_list')

# Redirection d'un parent
class ParentRedirectView(generic.RedirectView):
	
	def get_redirect_url(self, *args, **kwargs):
		user=self.request.user
		return reverse('parent_profile', args=[user.id])		


# Accueil / panneau de contrôle de l'admin - statique et entièrement défini
# par son HTML
class AdminIndexView(generic.TemplateView):
	template_name="garderie/admin_index.html"

# Liste des enfants, fournit tous les Child ainsi que chaque Schedule encore
# incomplet (départ indéterminé) et un Schedule proche (arrivée +- une heure)
class ChildrenListView(generic.ListView):
	template_name='garderie/children_list.html'
	context_object_name='children_list'

	def get_queryset(self):
		print("-------------")
		print(Child.objects.closest_expected_schedules())
		return {'all_children': Child.objects.all(), 
						'current_schedules': Schedule.objects.incomplete_schedules()
					 }
	

# Liste des parents, fournit au HTML tous les Parent
class ParentListView(generic.ListView):
	template_name="garderie/parent_list.html"
	context_object_name='parent_list'

	def get_queryset(self):
		return Parent.objects.all()


# Profil d'un enfant donné
class ChildProfileView(generic.DetailView):
	model=Child
	template_name='garderie/child_profile.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = NewScheduleForm(pk=self.kwargs['pk'])
		context['action']=reverse('schedule_register', kwargs={'pk':self.kwargs['pk']}) # même URL donc sûrement améliorable
		return context

# Profil d'un parent donné
class ParentProfileView(generic.DetailView):
	model=Parent
	template_name='garderie/parent_profile.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = NewChildFormParent(request=self.request)
		return context
	
# Formulaire de création d'un schedule
class CreateScheduleView(generic.edit.CreateView):
	form_class=NewScheduleForm
	template_name='garderie/forms/embedded_form.html' # TODO TODO
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
	


# Formulaire de création d'un nouvel enfant par l'admin
class NewChildView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_child.html'
	form_class = NewChildFormAdmin
	success_url = reverse_lazy('children_list') # TODO plutôt renvoyer sur le profil ?

	
# Formulaire de création d'un nouveau taux horaire
class NewHourlyRateView(generic.edit.CreateView):
	template_name='garderie/forms/new_child.html'
	form_class = NewHourlyRateForm
	success_url = reverse_lazy('admin_index')

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


# Formulaire de suppression d'un schedule
class ScheduleDeleteView(generic.edit.DeleteView):
#	template_name='garderie/child_garde	profile.html'
	model = Schedule
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page



# Formulaire de suppression d'un enfant
class ChildDeleteView(generic.edit.DeleteView):
	template_name='garderie/child_profile.html'
	model = Child
	
	def get_success_url(self):
		return self.request.GET.get('next', reverse('children_list')) # évite un changement de page


# Enregistre l'heure d'arrivée d'un enfant 
def AjaxChildUpdateArrival(request):
	child_id = request.POST.get('id', None)
	child=Child.objects.filter(pk=child_id)[0]
	child_name=child.first_name+" "+child.last_name
					
	try:
		if child.incomplete_schedule()!=None: # un schedule en cours 
			return JsonResponse({'error': "L'enfant est déjà présent."})
	except Schedule.DoesNotExist:
		print(f'DoesNotExist raised sur {child}')
		
	schedule=Schedule()
	schedule.arrival=timezone.now()
	schedule.child=child
	schedule.expected=False
	schedule.rate=HourlyRate.objects.latest('id')
	schedule.save()


	data = {
	'name': child_name,
	'arrival': schedule.arrival
	}
	
	
	# Récupère le schedule le plus proche  s'il y en a un
	closest=child.closest_expected_schedule(schedule)
	data['expected_arrival']=closest.arrival if closest else 'N/A'
	data['expected_departure']=closest.departure if closest else 'N/A'
	
	# check si l'enfant est encore présent (date de départ pas encore remplie)
	# Une exception peut avoir lieu s'il n'y a aucun Schedule associé à l'enfant, 
	# ce qui en ce qui nous concerne ici revient au même : enfant pas encore là.


	return JsonResponse(data)

# Enregistre l'heure de départ d'un enfant
def AjaxChildUpdateDeparture(request):
	child_id = request.POST.get('id', None)
	child=Child.objects.filter(pk=child_id)[0]
	child_name=child.fullname()
	
	try: # TODO mériterait un logging (jamais censé arriver)
		schedule=child.incomplete_schedule()
		print(f'Check {schedule}')
		if(schedule==None):
			return JsonResponse({'error': "L'enfant est déjà parti."})
	except Schedule.DoesNotExist:
		return JsonResponse({'error' : 'Erreur inconnue'})
	
	schedule.departure=timezone.now()
	schedule.save()
	
	data = {
	'name': child_name,
	'departure': schedule.departure
	}
	return JsonResponse(data)



#	def get_context_data(self, **kwargs):
#		context = super().get_context_data(**kwargs)
#		context['child'] = Child.objects.all()
#		return context


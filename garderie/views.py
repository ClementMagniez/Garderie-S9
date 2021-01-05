from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Child, Parent, HourlyRate, Schedule, ReliablePerson
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
		context['schedule_form'] = NewScheduleForm(pk=self.kwargs['pk'])
		context['action']=reverse('schedule_register', kwargs={'pk':self.kwargs['pk']}) # même URL donc sûrement améliorable
		context['personal_data_form'] = ChildUpdateForm(instance=self.object)	
		return context

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
	
# Formulaire d'édition d'un enfant donné, embedded dans ChildProfileView
class ChildUpdateView(generic.edit.UpdateView):
	form_class=ChildUpdateForm
	model = Child
	
	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		return kwargs
		
	def get_success_url(self):
		return reverse('child_profile', kwargs={'pk':self.kwargs['pk']})


	

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

# Formulaire de suppression d'une personne de confiance
class ParentDeleteReliableView(generic.edit.DeleteView):
	model = ReliablePerson
	
	def get_success_url(self):
		return reverse('parent_profile', kwargs={'pk':self.request.user.id})


# Enregistre l'heure d'arrivée d'un enfant 
def AjaxChildCreateArrival(request):
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
def AjaxChildCreateDeparture(request):
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
	'sid': schedule.id, # utilisé pour permettre l'édition de la date de départ de l'enfant
	'name': child_name, # utilisé pour l'affichage
	'departure': schedule.departure # utilisé pour l'affichage
	}
	return JsonResponse(data)


# Modifie l'heure de départ d'un schedule
# TODO TODO : ne valide pas le format de l'input avant la tentative de le save
# (transformer la prompt js en une modale contenant un form ?)
def AjaxChildEditDeparture(request):
	schedule_id = request.POST.get('id', None)
	schedule=Schedule.objects.filter(pk=schedule_id)[0]
	
	new_departure=request.POST.get('hour', None)
	try: 
		if(new_departure==None):
			return JsonResponse({'error': "La date de départ renseignée n'a pas été trouvée."})
		new_departure=timezone.make_aware(datetime.strptime(new_departure, '%Y-%m-%d %H:%M:%S'))
		if(new_departure<schedule.arrival):
			return JsonResponse({'error': "La date de départ renseignée est avant la date d'arrivée de l'enfant."})
	except ValueError:
		return JsonResponse({'error': "Veuillez entrer l'heure sous le format YYYY-MM-DD hh:mm:ss."})
	except Schedule.DoesNotExist:
		return JsonResponse({'error' : 'Erreur inconnue'})
		
	schedule.departure=new_departure
	schedule.save()
	
	data = {
	'sid': schedule.id, # utilisé pour permettre l'édition de la date de départ de l'enfant
	'name': schedule.child.first_name, # utilisé pour l'affichage
	'departure': schedule.departure # utilisé pour l'affichage
	}
	return JsonResponse(data)


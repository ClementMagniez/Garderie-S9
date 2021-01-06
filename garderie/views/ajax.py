from ..models import Child, HourlyRate, Schedule
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

# Contient les views répondant à une requête AJAX



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


from ..models import Child, HourlyRate, Schedule
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from ..utils import get_datetime_from_hhmm
# Contient les views répondant à une requête AJAX

# Enregistre l'heure d'arrivée d'un enfant 
def AjaxChildCreateArrival(request):
	child_id = request.POST.get('id', None)
	child=Child.objects.filter(pk=child_id)[0]


	# check si l'enfant est encore présent (date de départ pas encore remplie)
	# Une exception peut avoir lieu s'il n'y a aucun Schedule associé à l'enfant, 
	# ce qui en ce qui nous concerne ici revient au même : enfant pas encore là.
	try:
		if child.incomplete_schedule()!=None: # un schedule en cours 
			return JsonResponse({'error': "L'enfant est déjà présent."})
	except Schedule.DoesNotExist:
		print(f'DoesNotExist raised sur {child}')
		# TODO mais du coup, on renvoie quoi ?
		
	schedule=Schedule()
	schedule.arrival=timezone.localtime()
	schedule.child=child
	schedule.rate=HourlyRate.objects.latest('id')
	schedule.save()

	data = {
	'name': child.fullname(),
	'sid': schedule.id,
	'arrival': schedule.arrival
	}
	


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
	
	schedule.departure=timezone.localtime()
	schedule.save()
	
	data = {
	'sid': schedule.id, # utilisé pour permettre l'édition de la date de départ de l'enfant
	'name': child_name, # utilisé pour l'affichage
	'departure': schedule.departure # utilisé pour l'affichage
	}
	return JsonResponse(data)


# Modifie l'heure de départ d'un schedule

def AjaxChildEditDeparture(request):
	schedule_id = request.POST.get('id', None)
	schedule=Schedule.objects.filter(pk=schedule_id)[0]
	
	new_departure=get_datetime_from_hhmm(request.POST.get('hour', None))

	try: 
		if(new_departure==None):
			return JsonResponse({'error': "La date de départ renseignée n'a pas été trouvée."})
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
	'cid': schedule.child.id, # utilisé pour retrouver le row dans la table
	'name': schedule.child.first_name, # utilisé pour l'affichage
	'departure': schedule.departure # utilisé pour l'affichage
	}
	return JsonResponse(data)

# Supprime un Schedule donné par 'id'
def AjaxChildRemoveArrival(request):
	schedule_id = request.POST.get('id', None)

	try: 
		schedule=Schedule.objects.filter(pk=schedule_id)[0]
	except IndexError:
		return JsonResponse({'error' : 'L\'enfant a déjà été retiré de la liste de présence.'})
		
	schedule.delete()
	
	data = {
	'cid': schedule.child.id, # utilisé pour retrouver le row dans la table
	}
	return JsonResponse(data)



# Modifie l'heure d'arrivée d'un schedule
def AjaxChildEditArrival(request):
	schedule_id = request.POST.get('id', None)
	
	schedule=Schedule.objects.filter(pk=schedule_id)[0]
	
	new_arrival=get_datetime_from_hhmm(request.POST.get('hour', None))
	try: 
		if(new_arrival==None):
			return JsonResponse({'error': "La date d'arrivée renseignée n'a pas été trouvée."})

		print(new_arrival)
	
	except ValueError:
		return JsonResponse({'error': "Veuillez entrer l'heure sous le format hh:mm."})
	except Schedule.DoesNotExist:
		return JsonResponse({'error' : 'Erreur inconnue'})
		
	schedule.arrival=new_arrival
	schedule.save()
	
	data = {
	'sid': schedule.id, # utilisé pour permettre l'édition de la date de départ de l'enfant
	'cid': schedule.child.id, # utilisé pour retrouver le row dans la table
	'name': schedule.child.first_name, # utilisé pour l'affichage
	}
	return JsonResponse(data)

# Supprime un Schedule donné par 'id'
def AjaxChildRemoveArrival(request):
	schedule_id = request.POST.get('id', None)

	try: 
		schedule=Schedule.objects.filter(pk=schedule_id)[0]
	except IndexError:
		return JsonResponse({'error' : 'L\'enfant a déjà été retiré de la liste de présence.'})
		
	schedule.delete()
	
	data = {
	'cid': schedule.child.id, # utilisé pour retrouver le row dans la table
	}
	return JsonResponse(data)





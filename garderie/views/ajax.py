from ..models import Child, HourlyRate, Schedule, Bill
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from ..forms import EditScheduleForm
from ..utils import get_datetime_from_hhmm
from django.shortcuts import render
from django.urls import reverse
### Contient les views répondant à une requête AJAX

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
		pass # résultat attendu, pas un problème 
		
	schedule=Schedule()
	schedule.arrival=timezone.localtime()
	print(timezone.localtime())
	schedule.child=child
	schedule.rate=HourlyRate.objects.latest('id')
	schedule.save()

	data = {
	'name': child.first_name,
	'sid': schedule.id,
	'arrival': schedule.arrival
	}
	
	return JsonResponse(data)

# Enregistre l'heure de départ d'un enfant
def AjaxChildCreateDeparture(request):
	child_id = request.POST.get('id', None)
	child=Child.objects.get(pk=child_id)
	
	try: # TODO mériterait un logging (jamais censé arriver)
		schedule=child.incomplete_schedule()
		if(schedule==None):
			return JsonResponse({'error': f'{child.first_name} est déjà parti.'})
	except Schedule.DoesNotExist:
		return JsonResponse({'error' : 'Erreur inconnue'})
	
	schedule.departure=timezone.localtime()
	schedule.save()
	
	data = {
	'sid': schedule.id,
	'name': child.first_name,
	'departure': schedule.departure
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
			return JsonResponse({'error': f'La date de départ renseignée est avant la date d\'arrivée de {schedule.child.first_name}.'})
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
		return JsonResponse({'error' : f'{schedule.child.first_name} a déjà été retiré de la liste de présence.'})
		
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
			return JsonResponse({'error': "L'heure d'arrivée renseignée est invalide."})
		if(schedule.departure and new_arrival>schedule.departure):
			return JsonResponse({'error': "L'heure d'arrivée renseignée est après l'heure de départ renseignée."})
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

def AjaxShowBillModal(request):
	bill_id=request.POST.get('id', None)
	context={'bill':Bill.objects.get(pk=bill_id)}
	return render(request, 'garderie/include/admin_bills_modal.html', context)


def AjaxShowScheduleFormModal(request):
	schedule_id=request.POST.get('id', None)
	schedule=Schedule.objects.get(pk=schedule_id)
	context={'schedule':schedule,
					 'form':EditScheduleForm(instance=schedule, pk=schedule_id), 
					 'action':reverse('schedule_edit',  kwargs={'pk':schedule_id})}
	return render(request, 'garderie/include/child_schedule_modal.html', context)

def AjaxShowChildrenHereThisDay(request):
	day=request.POST.get('day', None)
	day=datetime.strptime(day, "%Y-%m-%d").date()
	schedules={}
	for child in Child.objects.filter(schedule__arrival__date=day).distinct():
		schedules[child]=child.schedules_this_day(day)
	
	print(schedules)
	context={'schedules_dict':schedules,
					 'day': day}
	
	return render(request, 'garderie/include/children_list_modal.html', context)


def AjaxShowBillsThisMonth(request):
	date=request.POST.get('date', None)
	date=datetime.strptime(date, '%Y-%m').date()
	month=date.month
	year=date.year
	
	bills=[b for b in Bill.objects.filter(month=month, year=year)]
	
	context={'bills_list':bills}
	
	return render(request, 'garderie/include/bills_table.html', context)



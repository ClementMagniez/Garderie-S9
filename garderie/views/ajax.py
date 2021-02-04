from ..models import Child, HourlyRate, Schedule, Bill, Config, Parent
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from ..forms import EditScheduleForm
from ..utils import get_datetime_from_hhmm
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import decorators
### Contient les views répondant à une requête AJAX

# Enregistre l'heure d'arrivée d'un enfant 
@decorators.user_passes_test(lambda u: u.is_staff)
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
@decorators.user_passes_test(lambda u: u.is_staff)
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

@decorators.user_passes_test(lambda u: u.is_staff)
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
@decorators.user_passes_test(lambda u: u.is_staff)
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
@decorators.user_passes_test(lambda u: u.is_staff)
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


def set_bill_modal_from_request(request):
	pid=request.POST.get('id', None)
	parent=Parent.objects.get(pk=pid)
	month=request.POST.get('month', "")
	year=request.POST.get('year', "")
	
	if month=="" or year=="":
		bills=parent.bill_set.all()
	else:		
		bills=parent.get_bills(month, year)
	context={'bills':(bills,sum(b.amount for b in bills)),
					 'parent':parent, 
					 'month':month, 'year':year}
	return context

def AjaxShowBillsModalAdmin(request):
	context=set_bill_modal_from_request(request)
	return render(request, 'garderie/include/admin_bills_modal.html', context)

def AjaxShowBillsModalParent(request):
	context=set_bill_modal_from_request(request)
	return render(request, 'garderie/include/parent_bills_modal.html', context)




@decorators.user_passes_test(lambda u: u.is_superuser)
def AjaxShowScheduleFormModal(request):
	schedule_id=request.POST.get('id', None)
	schedule=Schedule.objects.get(pk=schedule_id)
	context={'schedule':schedule,
					 'form':EditScheduleForm(instance=schedule, pk=schedule_id), 
					 'action':reverse('schedule_edit',  kwargs={'pk':schedule_id})}
	return render(request, 'garderie/include/child_schedule_modal.html', context)

@decorators.user_passes_test(lambda u: u.is_staff)
def AjaxShowChildrenHereThisDay(request):
	day=request.POST.get('day', None)
	day=datetime.strptime(day, "%Y-%m-%d").date()
	schedules={}
	for child in Child.objects.filter(schedule__arrival__date=day).distinct():
		schedules[child]=child.schedules_this_day(day)
	
	context={'schedules_dict':schedules,
					 'day': day}
	
	return render(request, 'garderie/include/children_list_modal.html', context)


# Renvoie un tuple (int, int) mois/an si request.POST.'date' est défini
# None, None sinon
def get_month_year_from_request(request):
	date=request.POST.get('date', None)
	try:
		date=datetime.strptime(date, '%m/%Y').date()
	except ValueError:
		return None, None

	return date.month, date.year

@decorators.user_passes_test(lambda u: u.is_superuser)
def AjaxSwapDisplayBillsAdmin(request):
	month, year=get_month_year_from_request(request)
	
	template='garderie/include/bills_table.html'
	context={}
	context['parents_list']=[]
	for parent in Parent.objects.all():
		if month:
			bills=parent.get_bills(month,year)
		else:
			bills=parent.bill_set.all()
		context['parents_list'].append({parent: (bills, sum(b.amount for b in bills))})

	return render(request, template, context)


def AjaxSwapDisplayBillsParent(request):
	month, year=get_month_year_from_request(request)
	pid=request.POST.get('pid', None)
	parent=Parent.objects.get(pk=pid)
	
	template='garderie/include/parent_bills_table.html'

	if month:
		bills=parent.get_bills(month, year)
	else:
		bills=parent.bill_set.all()
	context={'bills':bills}
	return render(request, template, context)

@decorators.user_passes_test(lambda u: u.is_superuser)
def AjaxShowRecapPresence(request):	
	month, year=get_month_year_from_request(request)
	
	template='garderie/include/bills_list_modal.html'
	if month:
		bills=[b for b in Bill.objects.filter(month=month, year=year).order_by('child__last_name')]
	else:
		bills=[b for b in Bill.objects.all().order_by('child__last_name')]
	context={'bills_list':bills}
	return render(request, template, context)

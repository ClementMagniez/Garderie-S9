import garderie.models
from django.utils import timezone

# Recense les fonctions utilitaires utilisées par d'autres fichiers de l'app



# Renvoie un Bill correspondant au même enfant, mois et an que schedule ;
# s'il n'existe pas, le crée
def get_or_create_bill(schedule):
	try:
		bill=garderie.models.Bill.objects.get(child=schedule.child,month=schedule.arrival.month, 
													year=schedule.arrival.year)
	except:
		bill=garderie.models.Bill(child=schedule.child)
		bill.save()
	return bill	
	
	
# Prend un string HH:MM et renvoie un objet Datetime initialisé à la date
# du jour, avec l'heure et la minute remplacées par le paramètre
def get_datetime_from_hhmm(hhmm):
	new_hhmm=hhmm.split(':')
	return timezone.now().replace(hour=int(new_hhmm[0]), minute=int(new_hhmm[1]))
	

def is_parent_permitted(view):
		return view.request.user.id==view.kwargs['pk'] or view.request.user.is_superuser

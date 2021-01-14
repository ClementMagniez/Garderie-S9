from .models import Schedule, Bill 


# Recense les fonctions utilitaires utilisées par d'autres fichiers de l'app



# Cherche un Bill correspondant au même mois et an que schedule
# S'il existe, en fait la foreign key de schedule
# Sinon, le crée et en fait la foreign key de schedule
def get_or_create_bill(schedule):
	
	try:
		bill=Bill.objects.get(child=schedule.child,month=schedule.arrival.month, 
													year=schedule.arrival.year)
	except:
		bill=Bill(child=schedule.child)
		bill.save()
	finally:
		schedule.bill=bill
		schedule.save()
	return bill	

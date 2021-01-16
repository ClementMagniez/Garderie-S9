import garderie.models


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

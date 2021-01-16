from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date, time
from math import ceil, floor
import garderie.utils 

# Managers

class ScheduleManager(models.Manager):

	# Schedules incomplets, sans départ encore déterminé
	def incomplete_schedules(self):
		return super().get_queryset().filter(departure=None)

	# Schedules ayant commencé il y a moins de 30 jours		
	def recent_schedules(self):
		return super().get_queryset().filter(arrival__gte=datetime.today()-timedelta(days=30))

class ChildManager(models.Manager):
	# Renvoie un array de Schedules où chaque schedule correspond à Child#closest_expected_schedule
	# pour chaque enfant existant
	def closest_expected_schedules(self):
		all_entries=super().all()
		
		res=[]
		for child in all_entries:
			res.append(child.closest_expected_schedule(child.incomplete_schedule()))
		return res	


	# Appelle Child#generate_bill sur chaque Child existant avec month et year 
	def generate_all_bills(self, month, year):
		for child in super().all():
			child.generate_bill(month, year)

### Modèles

class Parent(models.Model):
	uid=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	phone=models.CharField(max_length=20, null=True, verbose_name="Téléphone")


	def __str__(self):
		return self.uid.first_name+" "+self.uid.last_name
		
	def fullname(self):
		return str(self)			

class Child(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=100, null=True, verbose_name="Prénom")
	last_name=models.CharField(max_length=100, null=True, verbose_name="Nom")

	objects=ChildManager()

	def __str__(self):
		return self.first_name+" "+self.last_name
		
	### Méthodes de manipulation du modèle

	def fullname(self):
		return str(self)	

	# Renvoie un schedule incomplet (departure==None) de l'enfant ou None
	def incomplete_schedule(self):
		for schedule in self.schedule_set.all():
			if schedule.departure==None:
				return schedule

	#	Renvoie le Schedule de l'enfant le plus proche du schedule donné à 3h près, 
	# ou None s'il n'y en a pas 
	def closest_expected_schedule(self, schedule):
		
		# Cas qui ne devrait pas arriver en pratique ; au cas où, on crée un dummy Schedule
		# qui correspond à l'heure actuelle
		if schedule==None:
			schedule=Schedule(arrival=timezone.now(), departure=None)
			
		# on récupère un schedule en calculant celui dont l'arrivée est la
		# plus proche de l'arrivée réelle, à trois heures près
		greater=self.schedule_set.filter(expected=True, arrival__gte=schedule.arrival,
																		 arrival__lte=schedule.arrival+timedelta(hours=3))\
																		 .order_by('arrival').first()
		lesser=self.schedule_set.filter(expected=True, arrival__lte=schedule.arrival, 
																		arrival__gte=schedule.arrival-timedelta(hours=3))\
																		.order_by('-arrival').first()

		closest=None

		if greater and lesser:
			if abs(greater.arrival-schedule.arrival) < abs(lesser.arrival - schedule.arrival):
				closest=greater
			else: 
				closest=lesser
		else:
				closest=greater if greater else lesser
		return closest 
		
	# Permet de récupérer le dernier schedule incomplet (normalement unique) via 
	# incomplete_schedule et d'en chercher l'expected_schedule le plus proche via
	# closest_expected_schedule
	def closest_to_incomplete(self):
		ongoing=self.incomplete_schedule()
		if ongoing==None:
			return None
		else:
			return self.closest_expected_schedule(ongoing)

	# Schedules ayant commencé il y a moins de 30 jours		
	def recent_schedules(self):
		return self.schedule_set.filter(arrival__gte=datetime.today()-timedelta(days=30))

	# Schedules créés et anticipés, expected=True		
	def expected_schedules(self):
		return self.schedule_set.filter(expected=True)

	# Bill du mois courant, None s'il n'y en a pas
	def last_bill(self):
		today=timezone.now()
		bills=self.bill_set.filter(year=today.year, month=today.month)
			
		return bills[0] if bills else None


class HourlyRate(models.Model):
	value=models.FloatField(verbose_name="Taux horaire")
	date_start=models.DateTimeField("Date de départ")
	date_end=models.DateTimeField("Date de fin", null=True)
		
		
class Bill(models.Model):

	# Tuple "numéro dans la DB, valeur lisible" : on convertit donc le numéro en un string
	MONTH=[(m, date(1900, m, 1).strftime('%B'))  for m in range(1,13)]
	YEAR=[(y, date(y, 1,1).strftime('Y')) for y in range(2000,timezone.now().year+1)]


	child=models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name="Enfant associé")
	amount=models.FloatField(default=0, verbose_name="Montant total")
	month=models.IntegerField(choices=MONTH, default=timezone.now().month, verbose_name="Mois")
	year=models.IntegerField(choices=YEAR, default=timezone.now().year, verbose_name="Année")
			
	### Méthodes de manipulation du modèle

	
	# Return le coût d'un schedule 
	def calc_amount_from_schedule(self, schedule):
		arrival, departure=schedule.rounded_arrival_departure()
		duration=(departure-arrival).seconds/3600
		return round(duration*schedule.rate.value)	# round pour éliminer les millisecondes inutiles et avoir un int
	
	# Enregistre _amount_ à partir des Schedules associés à self
	def calc_amount(self):
		print("dans calc amunt")
		amount=0
		for schedule in self.schedule_set.all():
			print(str(schedule.id) + " " + str(schedule))
			amount+=self.calc_amount_from_schedule(schedule)
		self.amount=amount
		self.save()
		
		
class Schedule(models.Model):
	child=models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name="Enfant")
	rate=models.ForeignKey(HourlyRate, on_delete=models.CASCADE, null=True)
	arrival=models.DateTimeField('Heure d\'arrivée')
	departure=models.DateTimeField('Heure de départ', null=True)
	expected=models.BooleanField()
	recurring=models.BooleanField(verbose_name="Plage horaire répétitive", default=True)
	bill=models.ForeignKey(Bill, null=True, on_delete=models.DO_NOTHING)

	objects=ScheduleManager()

	def __str__(self):
		return str(self.arrival)+" -- "+str(self.departure)
		
	# Automatise l'interaction entre Schedule et Bill à l'ajout/édition du Schedule
	# Trois cas :
	# 1. Création du schedule : utils.get_or_create_bill lui attribue un Bill
	# 2. Edition de schedule.departure ou schedule.arrival : on recalcule la valeur de Bill 
	# 	 en prenant ce changement en commpte
	# 3. Edition d'un autre champ : on ne fait rien de particulier 
	def save(self, *args, **kwargs):
		old=Schedule.objects.filter(id=getattr(self,'id',None)).first()
		print("dans save")
		if not old:
			bill=garderie.utils.get_or_create_bill(self)
			self.bill=bill
		super().save()	
		if old:
			print("après old check")
			if old.arrival!=self.arrival or old.departure!=self.departure or not old.departure:
				print("après diff check, calcul montant : " +str(self.departure))
				self.bill.calc_amount()
	
	# Recalcule la facture associée après avoir supprimé self
	def delete(self, *args, **kwargs):
		print("dans delete")
		bill=self.bill
		super().delete()
		self.bill.calc_amount()
	
	### Méthodes de manipulation du modèle
	
	# Renvoie True si le schedule n'a pas encore de départ, False sinon
	def incomplete(self):
		return self.departure==None
		

	# Renvoie True si le schedule a commencé au cours des 30 derniers jours
	def in_past_month(self):
		last_month=datetime.today()-timedelta(days=30)
		return self.arrival>last_month

	# Renvoie un tuple d'int (arrival, departure) où arrival est 
	# arrondi à la demi-heure inférieure et departure à la demi-heure supérieure
	# par rapport aux heures réelles
	# Exemple : si le Schedule enregisre arrival=7:03 et departure=8:34, 
	# rounded_arrival_departure renverra (7:00, 8:30) 

	def rounded_arrival(self):
		temp_arrival=self.arrival
		arrival_minute=floor(self.arrival.minute/30)*30
		temp_arrival=self.arrival.replace(minute=arrival_minute)
		return temp_arrival

	def rounded_departure(self):
		if not self.departure: # peut arriver si l'enfant est actuellement présent
			return None
		temp_departure=self.departure				
		# Logique en cas où on arrondit à 60 : Datetime.minute accepte [0..59] 		
		departure_minute=ceil(self.departure.minute/30)*30
		departure_hour=self.departure.hour
		if departure_minute==60:
			departure_minute=0
			departure_hour+=1

		temp_departure=self.departure.replace(hour=departure_hour, minute=departure_minute)
		return temp_departure
		
	# Renvoie un tuple d'int (arrival, departure) ; voir Schedule#rounded_arrival
	# et Schedule#rounded_departure
	def rounded_arrival_departure(self):
		return (self.rounded_arrival(), self.rounded_departure())	
	
	# Ajoute la durée
	def update_bill(self):
		if not self.bill:
			return None
		self.bill.calc_amount()
		
			
	
# Personne de confiance : pas responsable légal d'un enfant, mais susceptible 
# d'aller le chercher et devant donc être connu	du système
# N'interagit pas directement avec le système
class ReliablePerson(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=100, verbose_name="Préom")
	last_name=models.CharField(max_length=100, verbose_name="Nom")
	phone=models.CharField(max_length=20, null=True, verbose_name="Téléphone") 

	def __str__(self):
		return self.first_name+" "+self.last_name

	def fullname(self):
		return str(self)	

	

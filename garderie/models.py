from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

# Managers

class ScheduleManager(models.Manager):

	# Schedules incomplets, sans départ encore déterminé
	def incomplete_schedules(self):
		return super().get_queryset().filter(departure=None)

	# Schedules ayant commencé il y a moins de 30 jours		
	def recent_schedules(self):
		return super().get_queryset().filter(arrival__gte=datetime.datetime.today()-datetime.timedelta(days=30))

class ChildManager(models.Manager):
	# Renvoie un array de Schedules où chaque schedule correspond à Child#closest_expected_schedule
	# pour chaque enfant existant
	def closest_expected_schedules(self):
		all_entries=super().all()
		
		res=[]
		for child in all_entries:
			res.append(child.closest_expected_schedule(child.incomplete_schedule()))
		
		return res	


# Modèles

class Parent(models.Model):
	uid=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	phone=models.CharField(max_length=20, null=True)


	def __str__(self):
		return self.uid.first_name+" "+self.uid.last_name
		
	def fullname(self):
		return str(self)			

class Child(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	last_name=models.CharField(max_length=100, null=True)
	first_name=models.CharField(max_length=100, null=True)

	objects=ChildManager()

	def __str__(self):
		return self.first_name+" "+self.last_name

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
		greater=self.schedule_set.filter(expected=True, arrival__gte=schedule.arrival, arrival__lte=schedule.arrival+datetime.timedelta(hours=3)).order_by('arrival').first()
		lesser=self.schedule_set.filter(expected=True, arrival__lte=schedule.arrival, arrival__gte=schedule.arrival-datetime.timedelta(hours=3)).order_by('-arrival').first()

		closest=None

		if greater and lesser: # TODO créer un comparateur à Schedule ?
			if abs(greater.arrival-schedule.arrival) < abs(lesser.arrival - schedule.arrival):
				closest=greater
			else: 
				closest=lesser
		else:
				closest=greater if greater else lesser
#		print(f'Greater : {greater}') 
#		print(f'Lesser : {lesser}')				
#		print(f'Closest expected : {closest}')
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


class HourlyRate(models.Model):
	value=models.FloatField()
	date_start=models.DateTimeField("Date de départ")
	date_end=models.DateTimeField("Date de fin", null=True)
		
class Schedule(models.Model):
	child=models.ForeignKey(Child, on_delete=models.CASCADE)
	rate=models.ForeignKey(HourlyRate, on_delete=models.CASCADE, null=True)
	arrival=models.DateTimeField('Heure d\'arrivée')
	departure=models.DateTimeField('Heure de départ', null=True)
	expected=models.BooleanField()
	recurring=models.BooleanField(default=True)

	objects=ScheduleManager()

	def __str__(self):
		return str(self.arrival)+" -- "+str(self.departure)
	
	# Renvoie True sile schedule n'a pas encore de départ, False sinon
	def incomplete(self):
		return self.departure==None
		

	# Renvoie True si le schedule a commencé au cours des 30 derniers jours
	def in_past_month(self):
		last_month=datetime.datetime.today()-datetime.timedelta(days=30)
		return self.arrival>last_month

	
class ReliablePerson(models.Model):
	parents=models.ForeignKey(Parent, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=100)
	last_name=models.CharField(max_length=100)
	phone=models.CharField(max_length=20, null=True) 

	def __str__(self):
		return self.first_name+" "+self.last_name


class Bill(models.Model):
	child=models.ForeignKey(Child, on_delete=models.CASCADE)
	rate=models.ForeignKey(HourlyRate, on_delete=models.DO_NOTHING)
	amount=models.FloatField()
	paid=models.BooleanField()
	date_start=models.DateTimeField("Date de départ")
	date_end=models.DateTimeField("Date de fin")
	

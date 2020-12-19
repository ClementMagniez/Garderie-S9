from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class Parent(models.Model):
	uid=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	phone=models.CharField(max_length=20, null=True)


	def __str__(self):
		return self.uid.first_name+" "+self.uid.last_name
		

class Child(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	last_name=models.CharField(max_length=100, null=True)
	first_name=models.CharField(max_length=100, null=True)

	def __str__(self):
		return self.first_name+" "+self.last_name
		

class HourlyRate(models.Model):
	value=models.FloatField()
	date_start=models.DateTimeField("Date de départ")
	date_end=models.DateTimeField("Date de fin", null=True)
		
class Schedule(models.Model):
	child=models.ForeignKey(Child, on_delete=models.CASCADE)
	rate=models.ForeignKey(HourlyRate, on_delete=models.CASCADE, null=True)
	arrival=models.DateTimeField('Heure d\'arrivée')
	departure=models.DateTimeField('Heure de départ')
	expected=models.BooleanField()
	recurring=models.BooleanField(default=True)

	def __str__(self):
		return str(self.arrival)+" -- "+str(self.departure)
		
	
	
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
	

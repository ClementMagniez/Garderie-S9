from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class Parent(models.Model):
	uid=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	phone=models.CharField(max_length=20, null=True) # on rajoutera des champs plus tard


	def __str__(self):
		return self.uid.first_name+" "+self.uid.last_name
		

class Child(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	name=models.CharField(max_length=100, null=True)
	surname=models.CharField(max_length=100, null=True)

	def __str__(self):
		return self.surname+" "+self.name
		
		
class Schedule(models.Model):
	child=models.ForeignKey(Child, on_delete=models.CASCADE)
	arrival=models.DateTimeField('Heure d\'arrivée') # ajouter un champ jour et la possiblité d'avoir une date ponctuelle
	departure=models.DateTimeField('Heure de départ')
	expected=models.BooleanField()

	def __str__(self):
		return str(self.arrival)+" -- "+str(self.departure)
		
		
		
class Config(models.Model):
	key=models.CharField(max_length=100, primary_key=True)
	value=models.CharField(max_length=100)

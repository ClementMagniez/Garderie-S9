from django.db import models
from django.utils import timezone
import datetime

class User(models.Model):
	login=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	privilege=models.IntegerField()
	
	def __str__(self):
		return self.login
								
class Parent(models.Model):
	uid=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	name=models.CharField(max_length=100, null=True)
	surname=models.CharField(max_length=100, null=True)
	phone=models.CharField(max_length=20, null=True)
	mail=models.CharField(max_length=100, null=True)

	def __str__(self):
		return self.surname+" "+self.name
								
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

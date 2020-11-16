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
	nom=models.CharField(max_length=100, null=True)
	prenom=models.CharField(max_length=100, null=True)
	telephone=models.CharField(max_length=20, null=True)
	mail=models.CharField(max_length=100, null=True)

	def __str__(self):
		return self.prenom+" "+self.nom
								
class Enfant(models.Model):
	parent=models.ForeignKey(Parent, on_delete=models.CASCADE)
	prenom=models.CharField(max_length=100, null=True)

class HorairesDePresence(models.Model):
	enfant=models.ForeignKey(Enfant, on_delete=models.CASCADE)
	arrivee=models.DateTimeField('Heure d\'arrivée')
	depart=models.DateTimeField('Heure de départ')
	prevu=models.BooleanField()

from django import forms
from django.core.mail import send_mail
from .models import Parent, Child, HourlyRate, Schedule
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime

import random
import string

# Sémantiqueemnt, on abuse un peu de ModelForm ici puisqu'on utilise un seul
# field de Parent ; en réalité, on crée un User, qu'on wrap dans la création d'un Parent 
# Concrètement, on économise les quelques lignes nécessaires à la création du Parent
class NewUserForm(forms.ModelForm):
	mail=forms.CharField(label="Adresse mail")
	first_name=forms.CharField(label="Prénom")
	last_name=forms.CharField(label="Nom")
	phone=forms.CharField(label="Téléphone")

	class Meta:
		model = Parent
		fields = [ 'phone']
	
	# Crée le nouvel utilisateur avec un mot de passe/login random, envoie un mail
	# à l'adresse renseignée avec les identifiants générés et crée le Parent lié
	# à cet User
	def save(self, commit=True):
		new_parent = super().save(commit=False)
		if commit:
		
			if(settings.DEBUG):
				random_username='test'
				random_password='test'
			else:
				random_username=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
				random_password= User.objects.make_random_password()			

			user=User.objects.create_user(username=random_username,
																		first_name=self.data.get('first_name'),
																		last_name=self.data.get('last_name'),
																		password=random_password,
																		email=self.data.get('mail'))
			user.save()
			new_parent.uid_id=user.id
			new_parent.save()
			send_mail('Bienvenue sur Garderie++', # TODO Message évidemment temporaire, à compléter
								'Voici vos identifiants :\nLogin : '+random_username+
								'\nMot de passe : '+random_password, 
								'a@b.com', 
								[user.email])
		return new_parent
		

# Formulaire de création d'un enfant par un admin
class NewChildFormAdmin(forms.ModelForm):
	class Meta:
		model = Child
		fields = [ 'parent', 'first_name', 'last_name']

# Formulaire de création d'un enfant par son parent 
# Par rapport à NewChildFormAdmin, masque le champ "parent"
# et le remplit automatiquement via l'utilisateur connecté
class NewChildFormParent(forms.ModelForm):
	class Meta:
		model = Child
		fields = ['first_name', 'last_name']

	def __init__(self, *args, **kwargs):
		self.request=kwargs.pop('request')
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		child=super().save(commit=False)
		if commit:
			child.parent_id=self.request.user.id
			child.save()
		return child
	
from django.contrib import messages
	
# Formulaire de création d'un Schedule pour un enfant donné
class NewScheduleForm(forms.ModelForm):
	class Meta:
		model = Schedule
		fields = [ 'arrival', 'departure']

	def __init__(self, *args, **kwargs):
		self.child=Child.objects.get(pk=kwargs.pop('pk'))
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		schedule=super().save(commit=False)
		if commit:
			schedule.child=self.child
			schedule.rate=HourlyRate.objects.all().latest('id')
			schedule.expected=True
			schedule.save()
		return schedule

	# On valide que le nouveau schedule n'overlap pas un ancien
	# Cas possibles : 
	# le nouveau fait partir l'enfant après qu'un autre l'ait fait arriver
	# un autre fait partir l'enfant après que le nouveau l'ait fait arriver
	def clean(self):
		cleaned_data = super().clean()
		
		new_arrival=cleaned_data.get('arrival')
		new_departure=cleaned_data.get('departure')

		if (new_arrival > new_departure):
			raise ValidationError("Le départ est avant l'arrivée.")			
		
		all_schedules_child=Schedule.objects.filter(child_id=self.child.id, expected=True)
		for schedule in all_schedules_child:
		
			if (schedule.arrival >= new_arrival and schedule.arrival <=	new_departure)\
		 	or (new_arrival <=	schedule.departure and new_arrival >= schedule.arrival):
				print('erreur de validation')
				print(f"new_arrival : {new_arrival} - comparaison : {schedule.arrival}")
				print(f"new_departure : {new_departure} - comparaison : {schedule.departure}")
				raise ValidationError("Le créneau voulu en chevauche un autre déjà existant.")
		return self.cleaned_data
			

class NewHourlyRateForm(forms.ModelForm):
	class Meta:
		model = HourlyRate
		fields = ['value']
		
	def save(self, commit=True):
		new_rate=super().save(commit=False)
		if commit:
			previous_rate=HourlyRate.objects.latest('id')
			if previous_rate != None:
				previous_rate.date_end=datetime.now()
			new_rate.date_start=datetime.now()
			previous_rate.save()
			new_rate.save()
		return new_rate

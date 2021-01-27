from django import forms
from django.core.mail import send_mail
from .models import Parent, Child, HourlyRate, Schedule, ReliablePerson, ExpectedPresence
from django.contrib.auth.models import User
from django.template import Context
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime

import random
import string

# Formulaire de création d'un Parent
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
		
			if settings.DEBUG:
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
			
			raw_data=get_template('garderie/email_welcome.txt')
			data_context=({'id':random_username, 'pw':random_password})
			text_data=raw_data.render(data_context)
			
			send_mail("Bienvenue sur Garderie++", text_data, 'a@b.com', [user.email])
		return new_parent
		
# Formulaire de modification d'un parent 
class ParentUpdateForm(forms.ModelForm):
# TODO : inverse complètement le raisonnement avec NewUserForm, qui prend
# pour modèle Parent et ajoute artificiellement User ; ici, on part de User
# et on ajoute User
# c'est fonctionnellement sans grande importance, mais à corriger éventuellement

	phone=forms.CharField(label="Téléphone")

	class Meta:
		model=User
		fields=['username', 'first_name', 'last_name', 'email']
		help_texts = { # TODO temporaire pour masquer l'aide par défaut, mais à compléter
				'username': None,
		}

	def __init__(self, *args, **kwargs):
		self.request=kwargs.pop('request')
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		updated_user=super().save(commit=False)
		if commit:
			parent=Parent.objects.get(uid=updated_user)
			parent.phone=self.cleaned_data['phone']
			parent.save()
			updated_user.save()
		return updated_user


# Formulaire de création d'un enfant par un admin
class NewChildFormAdmin(forms.ModelForm):
	class Meta:
		model = Child
		fields = [ 'parent', 'first_name', 'last_name']


# Formulaire de création d'une personne de confiance par un parent
class NewReliableForm(forms.ModelForm):
	class Meta:
		model = ReliablePerson
		fields = [ 'child', 'first_name', 'last_name']
		
	def __init__(self, *args, **kwargs):
		self.request=kwargs.pop('request')
		super().__init__(*args, **kwargs)
		self.fields['child'].queryset=Child.objects.filter(parent=self.request.user.id)
		
		
	def save(self, commit=True):
		person=super().save(commit=False)
		if commit:
			person.parent_id=self.request.user.id
			person.save()
		return person
				
		
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
	

# Met à jour un enfant
class ChildUpdateForm(forms.ModelForm):
	class Meta:
		model = Child
		fields = ['first_name', 'last_name']


# Formulaire de création d'un ExpectedPresence pour un enfant donné
class NewPresenceForm(forms.ModelForm):

	class Meta:
		model = ExpectedPresence
		fields = ['day', 'period']

	def __init__(self, *args, **kwargs):
		self.child=Child.objects.get(pk=kwargs.pop('pk'))
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		presence=super().save(commit=False)
		if commit:
			presence.child=self.child
			presence.save()
		return presence

	# On valide que le nouvel horaire n'overlap pas un ancien
	def clean(self):
		cleaned_data = super().clean()
		new_day=cleaned_data.get('day')
		new_period=cleaned_data.get('period')
				
		all_presences_child=ExpectedPresence.objects.filter(child_id=self.child.id)
		for presence in all_presences_child:
		
			if (presence.day==new_day and presence.period ==	new_period):
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

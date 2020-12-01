from django import forms
from django.core.mail import send_mail
from .models import Parent, Child, Config
from django.contrib.auth.models import User

from django.conf import settings


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
		

class NewChildForm(forms.ModelForm):
	class Meta:
		model = Child
		fields = [ 'parent', 'name', 'surname']
		

class EditHourlyRateForm(forms.ModelForm):
	class Meta:
		model = Config
		fields = [ 'value']

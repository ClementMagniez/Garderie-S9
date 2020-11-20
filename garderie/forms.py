from django import forms
from .models import Parent 
from django.contrib.auth.models import User

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
			user=User.objects.create_user(username='tes1t', # TODO générer un username random
																		first_name=self.data.get('first_name'),
																		last_name=self.data.get('last_name'),
																		password='test', # Users.objects.made_random_password()			
																		email=self.data.get('mail'))
			user.save()
			new_parent.uid_id=user.id
			new_parent.save()

		return new_parent

from django import forms
from .models import Parent, Child, HourlyRate, Schedule, ReliablePerson, ExpectedPresence
from django.contrib.auth.models import User
from django.template import Context
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime
from .utils import create_parent_and_send_mail

# Formulaire de création d'un Parent
# Sémantiqueemnt, on abuse un peu de ModelForm ici puisqu'on utilise un seul
# field de Parent ; en réalité, on crée un User, qu'on wrap dans la création d'un Parent 
# Concrètement, on économise les quelques lignes nécessaires à la création du Parent
class NewUserForm(forms.ModelForm):
	mail=forms.CharField(label="Adresse mail")
	first_name=forms.CharField(label="Prénom")
	last_name=forms.CharField(label="Nom")

	class Meta:
		model = Parent
		fields = [ 'phone']
	
	# Crée le nouvel utilisateur avec un mot de passe/login random, envoie un mail
	# à l'adresse renseignée avec les identifiants générés et crée le Parent lié
	# à cet User
	def save(self, commit=True):
		new_parent = super().save(commit=False)
		if commit:
			create_parent_and_send_mail(new_parent, 
																	self.data.get('first_name'),
																	self.data.get('last_name'), 
																	self.data.get('mail'))
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
	second_parent_mail=forms.CharField(label="Mail du deuxième parent (facultatif)", required=False)
	
	class Meta:
		model = Child
		fields = [ 'parent', 'first_name', 'last_name']

	# Valide que les deux parents diffèrent
	def clean(self):
		cleaned_data = super().clean()
		parent=cleaned_data.get('parent')
		second_mail=cleaned_data.get('second_parent_mail')
	
		if (parent.uid.email==second_mail):
				raise ValidationError("Les deux parents sont la même personne !")
		return self.cleaned_data


	def save(self, commit=True):
		new_child=super().save(commit=False)
		if commit:
			second_mail=self.data.get('second_parent_mail')
			if second_mail:
				try:
					second_parent=User.objects.get(email=second_mail)
					second_parent=Parent.objects.get(pk=second_parent.id)
				except User.DoesNotExist:
					second_parent=Parent()
					create_parent_and_send_mail(second_parent, '', '', second_mail)		
					second_parent.save()
				new_child.second_parent=second_parent
			
			new_child.save()
		return new_child
						
		
# Formulaire de création d'un enfant par son parent 
# Par rapport à NewChildFormAdmin, masque le champ "parent"
# et le remplit automatiquement via l'utilisateur connecté
class NewChildFormParent(forms.ModelForm):
	second_parent_mail=forms.CharField(label="Mail du deuxième parent (facultatif)", required=False)
	class Meta:
		model = Child
		fields = [ 'first_name', 'last_name']

	def __init__(self, *args, **kwargs):
		self.pid=kwargs.pop('pk')
		super().__init__(*args, **kwargs)

	# Valide que les deux parents diffèrent
	def clean(self):
		cleaned_data = super().clean()
		parent=Parent.objects.get(uid=self.pid)
		second_mail=cleaned_data.get('second_parent_mail')
	
		if (parent.uid.email==second_mail):
				raise ValidationError("Les deux parents sont la même personne !")
		return self.cleaned_data

	def save(self, commit=True):
		print("debut save")
		new_child=super().save(commit=False)
		if commit:
			print("debut commit")
			second_mail=self.data.get('second_parent_mail')
			if second_mail:
				try:
					second_parent=User.objects.get(email=second_mail)
					second_parent=Parent.objects.get(pk=second_parent.id)
				except User.DoesNotExist:
					second_parent=Parent()
					create_parent_and_send_mail(second_parent, '', '', second_mail)		
					second_parent.save()

				new_child.second_parent=second_parent
			new_child.parent_id=self.pid
			new_child.save()
			print("fin commit")
		print("avant return")
		return new_child	

		
		
# Formulaire de création d'une personne de confiance par un parent
class NewReliableForm(forms.ModelForm):
	class Meta:
		model = ReliablePerson
		fields = [ 'child','first_name', 'last_name']
		
	def __init__(self, *args, **kwargs):
		self.pid=kwargs.pop('pk')
		super().__init__(*args, **kwargs)
		parent=Parent.objects.get(uid=self.pid)
		self.fields['child'].queryset=parent.all_children()

		
	# Valide que la personne n'est pas déjà présente'
	def clean(self):
		cleaned_data = super().clean()
		child=cleaned_data.get('child')
		first_name=cleaned_data.get('first_name')
		last_name=cleaned_data.get('last_name')
	
		res=child.reliableperson_set.filter(first_name=first_name, last_name=last_name)
		if len(res)>0:
				raise ValidationError("Une personne du même nom est déjà inscrite pour cet enfant.")
		return self.cleaned_data

	def save(self, commit=True):
		person=super().save(commit=False)
		if commit:
			person.parent_id=self.pid
			person.save()
		return person

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

	# Valide que le nouvel horaire n'overlap pas un ancien
	def clean(self):
		cleaned_data = super().clean()
		new_day=cleaned_data.get('day')
		new_period=cleaned_data.get('period')
		print("t-----------------------est")
		all_presences_child=ExpectedPresence.objects.filter(child_id=self.child.id)
		for presence in all_presences_child:
		
			if (presence.day==new_day and presence.period == new_period):
				raise ValidationError("Le créneau voulu en chevauche un autre déjà existant.")
		return self.cleaned_data
			
	def save(self, commit=True):
		print("-----------------------test")
		presence=super().save(commit=False)
		if commit:
			presence.child=self.child
			presence.save()
		return presence




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

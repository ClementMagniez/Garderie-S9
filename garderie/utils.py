from garderie import models
from django.utils import timezone
from django.template.loader import get_template
from django.core.mail import send_mail

from datetime import datetime
import random
import string

from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView

### Recense les fonctions et classes utilitaires utilisées par d'autres fichiers de l'app

# Classe générique pour les formulaires intégrés à une autre view : retourne leurs erreurs
# sous forme JSon et retient la pk de la view principale
class EmbeddedCreateView(CreateView):
	template_name='garderie/forms/base_form.html' # inutile en pratique, embedded_form.js intercepte

	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['pk']=self.kwargs['pk']
		return kwargs
		
	def form_invalid(self, form):
		return JsonResponse(form.errors)
	
	def form_valid(self, form):
		self.object=form.save()
		return JsonResponse({})

class EmbeddedUpdateView(UpdateView):
	template_name='garderie/forms/base_form.html' # inutile en pratique, embedded_form.js intercepte

	def get_form_kwargs(self):
		kwargs=super().get_form_kwargs()
		kwargs['pk']=self.kwargs['pk']
		return kwargs
		
	def form_invalid(self, form):
		return JsonResponse(form.errors)
	
	def form_valid(self, form):
		print("form_valid")
		self.object=form.save()
		return JsonResponse({})


# Renvoie un Bill correspondant au même enfant, mois et an que schedule ;
# s'il n'existe pas, le crée
def get_or_create_bill(schedule):
	try:
		bill=models.Bill.objects.get(child=schedule.child,month=schedule.arrival.month, 
													year=schedule.arrival.year)
	except:
		bill=models.Bill(child=schedule.child)
		bill.save()
	return bill	
	
	
# Prend un string HH:MM et renvoie un objet Datetime initialisé à la date
# du jour, avec l'heure et la minute remplacées par le paramètre
def get_datetime_from_hhmm(hhmm):
	new_hhmm=hhmm.split(':')
	return timezone.make_aware(datetime.today().replace(hour=int(new_hhmm[0]), minute=int(new_hhmm[1])))
	
	
# Utilisé par PermissionsMixin pour valider l'accès d'un parent à une vue
def is_parent_permitted(view):
		return view.request.user.id==view.kwargs['pk'] or view.request.user.is_superuser
	

def get_config(param):
	return models.Config.objects.get(id=0).values(param)[0]

	
### Création de compte et envoi de mails
	
def send_mail_creation_account(mail, random_password):
	data_context=({'id':mail, 'pw':random_password})
	send_mail_to_user(mail, "Bienvenue sur Garderie++", 'garderie/email_welcome.txt', data_context)
	
def send_mail_to_user(mail, subject, template, data):
	raw_data=get_template(template)
	text_data=raw_data.render(data)
	send_mail(subject, text_data, 'a@b.com', [mail])

		
def create_parent_and_send_mail(new_parent, first_name, last_name, mail):
	random_password=models.User.objects.make_random_password()			

	user=models.User.objects.create_user(
																first_name=first_name,
																last_name=last_name,
																password=random_password,
																email=mail)
	user.save()
	new_parent.uid_id=user.id
	new_parent.save()
	
	send_mail_creation_account(mail, random_password)

	return new_parent


def reset_password_send_mail(user):
	new_password=models.User.objects.make_random_password()
	user.set_password(new_password)
	user.save()
	data_context={'password':new_password}
	send_mail_to_user(user.email, "Votre nouveau mot de passe", 'garderie/email_reset_password.txt', data_context)

import garderie.models
from django.utils import timezone
from django.contrib.auth.models import User

from django.template.loader import get_template
from django.core.mail import send_mail
import random
import string

from django.http import JsonResponse
from django.views.generic.edit import CreateView

### Recense les fonctions et classes utilitaires utilisées par d'autres fichiers de l'app

# Classe générique pour les formulaires intégrés à une autre view : retournent leurs erreurs
# sous forme JSon et retiennent la pk de la view principale
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



# Renvoie un Bill correspondant au même enfant, mois et an que schedule ;
# s'il n'existe pas, le crée
def get_or_create_bill(schedule):
	try:
		bill=garderie.models.Bill.objects.get(child=schedule.child,month=schedule.arrival.month, 
													year=schedule.arrival.year)
	except:
		bill=garderie.models.Bill(child=schedule.child)
		bill.save()
	return bill	
	
	
# Prend un string HH:MM et renvoie un objet Datetime initialisé à la date
# du jour, avec l'heure et la minute remplacées par le paramètre
def get_datetime_from_hhmm(hhmm):
	new_hhmm=hhmm.split(':')
	return timezone.now().replace(hour=int(new_hhmm[0]), minute=int(new_hhmm[1]))
	
	
	
def is_parent_permitted(view):
		return view.request.user.id==view.kwargs['pk'] or view.request.user.is_superuser
	
	
		
def create_parent_and_send_mail(new_parent, first_name, last_name, mail):
#	if settings.DEBUG:
#		random_username='test'
#		random_password='test'
#	else:
	random_username=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
	random_password= User.objects.make_random_password()			

	user=User.objects.create_user(username=random_username,
																first_name=first_name,
																last_name=last_name,
																password=random_password,
																email=mail)
	user.save()
	new_parent.uid_id=user.id
	new_parent.save()

	raw_data=get_template('garderie/email_welcome.txt')
	data_context=({'id':random_username, 'pw':random_password})
	text_data=raw_data.render(data_context)

	send_mail("Bienvenue sur Garderie++", text_data, 'a@b.com', [user.email])
	return new_parent

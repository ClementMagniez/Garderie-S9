from django.test import TestCase
from garderie.forms import NewScheduleForm
from garderie.models import Parent


# Vérifie les validateurs d'un Schedule
class ScheduleFormSet(TestCase):	

	# vérifie qu'un Schedule est bien créé
	def test_schedule_form(self):
		print("???")
		# arrivée > départure
#		arrival='2020-01-01 10:10:10'
#		departure='2020-01-01 09:09:09'

#		form=NewScheduleForm(data={'arrival':arrival, 'departure':departure})
#		form.clean()
#		print(form.errors)
#		self.assertEquals(forms.errors, None)

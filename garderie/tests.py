from django.test import TestCase

from garderie.models import *
from datetime import datetime

from django.utils import timezone
from garderie.utils import *
# Vérifie le calcul d'une facture
class BillTests(TestCase):
	# Crée un parent, un HourlyRate et un enfant auxquels on peut rattacher cinq Schedules
	def setUp(self):
		user=User.objects.create_user(
																	first_name='test',
																	last_name='test',
																	password='test',
																	email='test@test.test')

		parent=Parent(uid=user, phone="16518612")
		parent.save()
		child=Child(parent=parent, first_name="foo", last_name="bar")
		child.save()
		h=HourlyRate(value=10, date_start=datetime.strptime('2020-01-01 01:00:00', "%Y-%m-%d %H:%M:%S"))
		h.save()

		self.bill=Bill(child=child, month=1, year=2020)
		self.bill.save()
	
		Schedule(child=child, bill=self.bill, rate=h, arrival=datetime.strptime('2020-01-01 11:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-01-01 11:30:00', "%Y-%m-%d %H:%M:%S")).save()
		self.schedule=Schedule(child=child, bill=self.bill, rate=h, arrival=datetime.strptime('2020-01-02 08:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-01-02 9:30:00', "%Y-%m-%d %H:%M:%S"))
		self.schedule.save()
		
	def testCalcAmount(self):
		self.assertEqual(len(self.bill.schedule_set.all()), 2)
		self.assertEqual(self.bill.amount, 40)
		self.bill.schedule_set.all()[0].delete()
		self.assertEqual(self.bill.amount, 30)


	def testGetCreateBill(self):
		# Cas 1 : Schedule créé dans une date correspondant à un Bill existant
		s=Schedule(child=self.schedule.child, rate=self.schedule.rate, arrival=datetime.strptime('2020-01-10 11:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-01-10 11:30:00', "%Y-%m-%d %H:%M:%S"))
		s.save()
		self.assertEqual(s.bill, self.bill)
		
		# Cas 2 : Schedule créé dans une date ne correspondant pas à un Bill existant
		s=Schedule(child=self.schedule.child, rate=self.schedule.rate, arrival=datetime.strptime('2020-02-10 11:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-02-10 11:30:00', "%Y-%m-%d %H:%M:%S"))
		s.save()
		self.assertNotEqual(s.bill, self.bill)


# Vérifie les fonctions utilitaires distinctes de la DB
class UtilsTests(TestCase):

	def testHHMM(self):
		res=get_datetime_from_hhmm('18:20')
		self.assertEqual(res.day,timezone.now().day)
		self.assertEqual(res.hour,18)
		self.assertEqual(res.minute,20)

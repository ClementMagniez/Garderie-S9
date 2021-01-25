from django.test import TestCase

from garderie.models import *
from django.contrib.auth.models import User
from datetime import datetime

class BillTests(TestCase):
	# Crée un parent, un HourlyRate et un enfant auxquels on peut rattacher cinq Schedules
	def setUp(self):
		user=User.objects.create_user(username='test',
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

		self.b=Bill(child=child, month=1, year=2020)
		self.b.save()
	
		Schedule(child=child, bill=self.b, rate=h, arrival=datetime.strptime('2020-01-01 11:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-01-01 11:30:00', "%Y-%m-%d %H:%M:%S")).save()
		Schedule(child=child, bill=self.b, rate=h, arrival=datetime.strptime('2020-01-02 08:00:00', "%Y-%m-%d %H:%M:%S"), departure=datetime.strptime('2020-01-02 9:30:00', "%Y-%m-%d %H:%M:%S")).save()
		
	def testCalcAmount(self):
		self.assertEqual(len(self.b.schedule_set.all()), 2)
		self.b.calc_amount()
		self.assertEqual(self.b.amount, 20)
	

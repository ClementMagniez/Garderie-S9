from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Manager
import garderie.models as models

class UserManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
			if not email:
					raise ValueError('L\'email doit être renseigné.')
			email = self.normalize_email(email)
			user = self.model(email=email, **extra_fields)
			user.set_password(password)
			user.save(using=self._db)
			return user

	def create_user(self, email, password=None, **extra_fields):
			extra_fields.setdefault('is_superuser', False)
			extra_fields.setdefault('is_staff', False)
			return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
			extra_fields.setdefault('is_superuser', True)
			extra_fields.setdefault('is_staff', True)
			if extra_fields.get('is_superuser') is not True:
					raise ValueError('Superuser must have is_superuser=True.')

			return self._create_user(email, password, **extra_fields)
			
class ConfigManager(Manager):
	def get_config(self):
		try:
			config=super().get_queryset()[0]
		except models.Config.DoesNotExist:
			config=models.Config()
			config.save()
		return config		
				

class ScheduleManager(Manager):

	# Schedules incomplets, sans départ encore déterminé
	def incomplete_schedules(self):
		return super().get_queryset().filter(departure=None)

	# Schedules ayant commencé il y a moins de 30 jours		
	def recent_schedules(self):
		return super().get_queryset().filter(arrival__gte=datetime.today()-timedelta(days=30))



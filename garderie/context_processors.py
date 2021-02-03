from .models import Config
def settings_processor(request):
	return {'settings':Config.objects.get_config()}

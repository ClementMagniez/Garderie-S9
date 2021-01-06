from django.views import generic
from ..forms import NewHourlyRateForm
from django.urls import reverse_lazy

# Contient les views concernant l'administrateur du site


# Accueil / panneau de contrôle de l'admin - statique et entièrement défini par son HTML
class AdminIndexView(generic.TemplateView):
	template_name="garderie/admin_index.html"

# Formulaire de création d'un nouveau taux horaire
class NewHourlyRateView(generic.edit.CreateView):
	template_name='garderie/forms/new_child.html'
	form_class = NewHourlyRateForm
	success_url = reverse_lazy('admin_index')



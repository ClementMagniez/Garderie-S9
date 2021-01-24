from django.views import generic
from ..forms import NewHourlyRateForm
from ..models import Bill, HourlyRate
from django.urls import reverse_lazy

# Contient les views concernant l'administrateur du site


# Accueil / panneau de contrôle de l'admin - statique et entièrement défini par son HTML
class AdminIndexView(generic.TemplateView):
	template_name="garderie/admin_index.html"

# Formulaire de création d'un nouveau taux horaire
class NewHourlyRateView(generic.edit.CreateView):
	template_name='garderie/forms/edit_rate_form.html'
	form_class = NewHourlyRateForm
	success_url = reverse_lazy('admin_index')
	
	def get_initial(self):
		initial=super().get_initial()
		initial['value']=HourlyRate.objects.latest('id').value
		return initial


# Liste des factures par ordre de date décroissante, fournit au HTML tous les Bills
class BillsListView(generic.ListView):
	template_name="garderie/bills_list.html"
	context_object_name='bills_list'

	def get_queryset(self):
		return Bill.objects.all().order_by('-month')


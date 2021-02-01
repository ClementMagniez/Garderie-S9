from django.views import generic
from ..forms import NewHourlyRateForm, NewUserForm, NewStaffForm, ResetPasswordForm
from ..models import Bill, HourlyRate, Parent, User
from django.urls import reverse_lazy
from ..utils import reset_password_send_mail
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

# Liste des parents
class ParentListView(generic.ListView):
	template_name="garderie/parent_list.html"
	context_object_name='parent_list'
	def get_queryset(self):
		return Parent.objects.all()

# Formulaire de création d'un nouveau parent
class NewUserView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_user.html'
	form_class = NewUserForm
	success_url = '/parent/'
	
	

# Formulaire de suppression d'un utilisateur
class UserDeleteView(generic.edit.DeleteView):
	model = User
	success_url = reverse_lazy('admin_index')
	
	# Interdit la suppression de son propre compte
	def delete(self, request, *args, **kwargs):
		user=self.get_object()
		if user.email==request.user.email:
			pass # TODO renvoyer une erreur TODO
#			return ('Vous ne pouvez pas supprimer votre propre compte !')
		else:
			return super().delete(self, request, *args, **kwargs)
		return HttpResponseRedirect(self.success_url)
	

class ResetPasswordView(generic.edit.FormView):
	template_name="garderie/forms/reset_password.html"
	form_class=ResetPasswordForm
	success_url=reverse_lazy('admin_index')


	def form_valid(self, form):
		user=form.cleaned_data['user']
#		if not user:
#			return JsonResponse({'error':'Aucun utilisateur n\'a été sélectionné.'})
	
		reset_password_send_mail(user)
		
		return super().form_valid(form)

# Formulaire de création d'un nouveau parent
class NewStaffView(generic.edit.CreateView):
	template_name = 'garderie/forms/new_user.html'
	form_class = NewStaffForm
	success_url = reverse_lazy('admin_index')	

# Liste des parents
class StaffListView(generic.ListView):
	template_name="garderie/staff_list.html"
	context_object_name='user_list'
	
	def get_queryset(self):
		return User.objects.filter(is_staff=True)

# Liste des factures par ordre de date décroissante, fournit au HTML tous les Bills
class BillsListView(generic.ListView):
	template_name="garderie/bills_list.html"
	context_object_name='bills_list'

	def get_queryset(self):
		return Bill.objects.all().order_by('-month')


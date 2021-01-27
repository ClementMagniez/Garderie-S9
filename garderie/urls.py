from django.urls import path
from django.contrib.auth.decorators import permission_required
from . import views

url_admin=[
        path('admin/tauxhoraire/',  permission_required('is_superuser')(views.NewHourlyRateView.as_view()), name='hourly_rate_form'),
        path('admin/factures',  permission_required('is_superuser')(views.BillsListView.as_view()), name='bills_list'),
        path('parent/', permission_required('is_superuser')(views.ParentListView.as_view()), name='parent_list'),
        path('parent/add/', permission_required('is_superuser')(views.NewUserView.as_view()), name='add_parent'),

]
url_parent=[
        path('parent-redirect/', views.ParentRedirectView.as_view(), name='parent_index'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('parent/<int:pk>/create_child/', views.ParentCreateChildView.as_view(), name='parent_create_child'),
        path('parent/<int:pk>/create_reliable/', views.CreateReliableView.as_view(), name='parent_create_reliable'),
        path('parent/<int:pk>/update/', views.ParentUpdateView.as_view(), name='parent_update'),
        path('parent/<int:pk>/delete/',  permission_required('is_superuser')(views.ParentDeleteView.as_view()), name='parent_delete'),
        path('parent/<int:pk>/delete_reliable/', views.ParentDeleteReliableView.as_view(), name='reliable_person_delete'),
]

url_enfant=[
        path('enfant/', views.ChildrenListView.as_view(), name='children_list'),
        path('enfant/add/', views.NewChildView.as_view(), name='add_child'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('enfant/<int:pk>/update/', views.ChildUpdateView.as_view(), name='child_update'),
        path('enfant/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child_delete'),
        path('enfant/<int:pk>/presence/register/', views.CreatePresenceView.as_view(), name='schedule_register'),
        path('enfant/<int:fk>/presence/<int:pk>/delete/', views.PresenceDeleteView.as_view(), name='presence_delete'),
        path('enfant/<int:fk>/schedule/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
]

url_ajax=[
        path('ajax/enter_hour_arrival/',  permission_required('is_staff')(views.AjaxChildCreateArrival), name='ajax_arrival'),
        path('ajax/enter_hour_departure/',  permission_required('is_staff')(views.AjaxChildCreateDeparture), name='ajax_departure'),
        path('ajax/edit_hour_arrival/',  permission_required('is_staff')(views.AjaxChildEditArrival), name='ajax_edit_arrival'),
        path('ajax/edit_hour_departure/',  permission_required('is_staff')(views.AjaxChildEditDeparture), name='ajax_edit_departure'),
        path('ajax/remove_arrival/',  permission_required('is_staff')(views.AjaxChildRemoveArrival), name='ajax_remove_arrival'),
]


url_redirect=[
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/accueil/', views.AdminIndexView.as_view(), name='admin_index'),
        path('educ-redirect/', views.EducRedirectView.as_view(), name='educ_index'),
]


urlpatterns = [ 
        path('', views.HomeRedirectView.as_view(), name='home_redirect'),
] + url_admin + url_parent + url_enfant + url_ajax + url_redirect


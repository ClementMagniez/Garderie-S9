from django.urls import path
from . import views

urlpatterns = [ 
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/accueil/', views.AdminIndexView.as_view(), name='admin_index'),
        path('educ-redirect/', views.EducRedirectView.as_view(), name='educ_index'),
        path('parent-redirect/', views.ParentRedirectView.as_view(), name='parent_index'),
        path('parent/', views.ParentListView.as_view(), name='parent_list'),
        path('parent/add/', views.NewUserView.as_view(), name='add_parent'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('parent/<int:pk>/create/', views.ParentCreateChildView.as_view(), name='parent_create_child'),
        path('parent/<int:pk>/update/', views.ParentUpdateView.as_view(), name='parent_update'),
        path('parent/<int:pk>/delete/', views.ParentDeleteView.as_view(), name='parent_delete'),
        path('enfant/', views.ChildrenListView.as_view(), name='children_list'),
        path('enfant/add/', views.NewChildView.as_view(), name='add_child'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('enfant/<int:pk>/update/', views.ChildUpdateView.as_view(), name='child_update'),
        path('enfant/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child_delete'),
        path('enfant/<int:pk>/schedule/register/', views.CreateScheduleView.as_view(), name='schedule_register'),
        path('enfant/<int:fk>/schedule/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
        path('admin/tauxhoraire/', views.NewHourlyRateView.as_view(), name='hourly_rate_form'),
        path('ajax/enter_hour_arrival/', views.AjaxChildCreateArrival, name='ajax_arrival'),
        path('ajax/enter_hour_departure/', views.AjaxChildCreateDeparture, name='ajax_departure'),
        path('ajax/edit_hour_departure/', views.AjaxChildEditDeparture, name='ajax_edit_departure'),
]


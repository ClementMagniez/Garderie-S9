from django.urls import path
from . import views

urlpatterns = [ 
        path('enfant/', views.ChildrenListView.as_view(), name='children_list'),
        path('parent/', views.ParentListView.as_view(), name='parent_list'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('parent/<int:pk>/delete/', views.ParentDeleteView.as_view(), name='parent_delete'),
        path('parent/<int:pk>/create/', views.ParentCreateChildView.as_view(), name='parent_create_child'),
        path('enfant/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child_delete'),
        
        path('enfant/<int:pk>/register/', views.CreateScheduleView.as_view(), name='child_register'),

        path('parent/add/', views.NewUserView.as_view(), name='add_parent'),
        path('enfant/add/', views.NewChildView.as_view(), name='add_child'),
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/accueil/', views.AdminIndexView.as_view(), name='admin_index'),
        path('educ-redirect/', views.EducRedirectView.as_view(), name='educ_index'),
        path('parent-redirect/', views.ParentRedirectView.as_view(), name='parent_index'),
        path('admin/tauxhoraire/', views.NewHourlyRateView.as_view(), name='hourly_rate_form'),
        path('ajax/enter_hour_arrival/', views.AjaxChildUpdateArrival, name='ajax_arrival'),
        path('ajax/enter_hour_departure/', views.AjaxChildUpdateDeparture, name='ajax_departure'),
]


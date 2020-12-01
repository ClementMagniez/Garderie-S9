from django.urls import path
from . import views

urlpatterns = [ 
        path('enfant/', views.ChildrenListView.as_view(), name='children_list'),
        path('parent/', views.ParentListView.as_view(), name='parent_list'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('parent/<int:pk>/delete/', views.ParentDeleteView.as_view(), name='parent_delete'),
        path('enfant/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child_delete'),
        path('parent/add/', views.NewUserView.as_view(), name='add_parent'),
        path('enfant/add/', views.NewChildView.as_view(), name='add_child'),
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/accueil/', views.AdminIndexView.as_view(), name='admin_index'),
        path('educ-redirect/', views.EducRedirectView.as_view(), name='educ_index'),
        path('parent-redirect/', views.ParentRedirectView.as_view(), name='parent_index'),
        path('admin/<slug:pk>', views.HourlyRateEditView.as_view(), name='hourly_rate_form'),
]


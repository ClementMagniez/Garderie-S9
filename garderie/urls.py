from django.urls import path
from . import views

urlpatterns = [ 
        path('enfant/', views.ChildListView.as_view(), name='child_list'),
        path('parent/', views.ParentListView.as_view(), name='parent_list'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('parent/<int:pk>/delete/', views.ParentDeleteView.as_view(), name='parent_delete'),
        path('parent/add/', views.NewUserView.as_view(), name='add_parent'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/', views.AdminIndexView.as_view(), name='admin_index'),
]


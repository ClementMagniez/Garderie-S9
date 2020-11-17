from django.urls import path
from . import views

urlpatterns = [ 
        path('index/', views.ListChildrenView.as_view(), name='index'),
        path('enfant/<int:pk>/', views.ChildProfileView.as_view(), name='child_profile'),
        path('parent/<int:pk>/', views.ParentProfileView.as_view(), name='parent_profile'),
        path('index-redirect/', views.IndexRedirectView.as_view(), name='index_redirect'),
        path('admin/', views.AdminIndexView.as_view(), name='admin_view'),
]


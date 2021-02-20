from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processing', views.processing, name='processing'),
    path('dataset/<int:dataset_id>/', views.dataset_info, name='dataset_info'),
    path('documentation/', views.documentation, name='documentation'),
    path('search', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('results/download/', views.download, name='download'),
]
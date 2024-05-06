from django.urls import path
from movies.api.v1 import views

urlpatterns = [
    path('admin_panel/movies/', views.MoviesListApi.as_view()),
    path('admin_panel/movies/<uuid:pk>/', views.MoviesDetailApi.as_view())
]

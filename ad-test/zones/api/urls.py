from django.urls import path


from zones.api import views

urlpatterns = [
    path('zones/edit', views.edit),
     path('zones/<int:zone_id>/', views.get_zone, name='zone_detail'),# incluyo la peticion de get
]
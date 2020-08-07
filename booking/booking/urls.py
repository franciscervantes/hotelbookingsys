"""booking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bookingApp import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'booking'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('book/',views.book, name='book'),
    path('staff/login/', views.adminLogin, name='admin_login'),
    path('staff/dashboard/', views.adminDash, name='admin_dash'),
    path('staff/reservation-list/', views.reservations, name="reservation_list"),
    path('staff/roomtype-list/', views.roomtypes, name="roomtype_list"),
    path('staff/room-list/', views.room, name="room_list"),
    path('staff/create/room/', views.createRoom,name='create_room'),
    path('staff/edit/roomtype/<int:room_type_id>/', views.editRoomtype,name='edit_roomtype'),
    path('staff/edit/room/<int:room_id>/', views.editRoom,name='edit_room'),
    path('staff/delete/room/<int:room_id>/', views.deleteRoom,name='delete_room'),
    path('staff/delete/roomtype/<int:room_type_id>/', views.deleteRoomtype,name='delete_roomtype'),
    path('staff/create/roomtype/', views.createRoomtype,name='create_roomtype'),
    path('staff/delete/<int:reservation_id>/', views.deleteReservation, name='delete_reservation'),
    path('staff/logout',views.adminLogout, name='admin_logout'),
    path('staff/edit/<int:reservation_id>/', views.editReservation,name='edit_reservation'),
    path('request-availability/',views.requestAvailability, name='request_availability'),
    path('create-reservation/',views.createReservation, name='create_reservation'),
    


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

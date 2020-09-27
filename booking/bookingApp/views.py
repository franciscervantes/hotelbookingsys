from django.shortcuts import render,redirect, get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
import json
from xhtml2pdf import pisa 
from datetime import datetime
import os
from tempfile import mkstemp
from django.conf import settings
from io import StringIO, BytesIO
import cgi

#create booking system admin
from django.contrib.auth.models import User
user = User.objects.create_user(username = 'admin1234', password ='admin')

#render homepage with room type objects
def homepage(request):
	roomtypes = RoomType.objects.all()
	return render(request, 'public_user/base/home.html', {'roomtypes':roomtypes})
#render user booking page with forms generated from django forms and roomtype objects
def book(request):
	reservation_form = ReservationForm(request.POST or None)
	room_type = RoomType.objects.all()
	status = ""
	return render(request, 'public_user/book/book.html', {'reservation_form': reservation_form, 'room_type': room_type })

#check the availability of rooms based on a given range of dates
#the check function excludes passed reservations when accessed through the edit function
def check_availability(rooms, date_in, date_out, reservation_id):
	for room in rooms:
		date_out_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_in, date_out__gte=date_in).exclude(pk=reservation_id).exists()
		date_in_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_out, date_out__gte=date_out).exclude(pk=reservation_id).exists()
		date_intersect = Reservation.objects.filter(room_id=room, date_in__gte=date_in, date_out__lte=date_out).exclude(pk=reservation_id).exists()
		if not(date_out_intersect or date_in_intersect or date_intersect):
			return room
	return None
#return room availability as a response to ajax calls
@csrf_exempt
def requestAvailability(request):
	if request.method == 'POST':

		date_in = request.POST.get("date_in")
		date_out = request.POST.get("date_out")
		room_id = request.POST.get("room_id")
		rooms = Room.objects.filter(room_type_id = room_id)

		if check_availability(rooms,date_in,date_out):
			response = {'status' : 'available'}
		else:
			response = {'status' : 'unavailable'}
		return JsonResponse(response)
#get number of days based on a given range
def get_days(date_in, date_out):
	date_format = "%Y-%m-%d"
	a = datetime.strptime(date_in, date_format)
	b = datetime.strptime(date_out, date_format)
	delta = b - a
	return delta.days 
#create user reservation if room is available for the selected dates
#returns user-friendly modals for either success or failed attempts at booking
def createReservation(request):
	if request.method == 'POST':
		data = dict()
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		client_email = request.POST.get('client_email')
		client_phone = request.POST.get('client_phone')
		date_in = request.POST.get('date_in')
		date_out = request.POST.get('date_out')
		room_id = request.POST.get('room_id')
		rooms = Room.objects.filter(room_type_id = room_id)
		days = get_days(date_in,date_out)
		price = get_object_or_404(RoomType, pk=room_id).price
		total_payment = days * price
		available_room = check_availability(rooms,date_in,date_out,None)
		reservation = Reservation(
        		first_name = first_name,
        		last_name = last_name,
        		client_email =client_email,
        		client_phone = client_phone,
             	date_in = date_in, 
             	date_out = date_out,
             	room_id = available_room,
             	days=days,
             	total_payment=total_payment,
             	)
		

		if available_room:
			
			reservation.save()
			context = {'reservation': reservation}
			data['status'] = 'created'
			data['html_form'] = render_to_string('public_user/book/payment_details.html', context, request=request)
	
			
		else:
			if rooms:
				roomExists = True
			else:
				roomExists = False

			context = {'reservation': reservation, 'roomExists':roomExists}
			data['html_form'] = render_to_string('public_user/book/booking_error.html',context, request=request)
			data['status'] = 'invalid'
		return JsonResponse(data)
#returns the absolute path of static urls of the project
def fetch_resources(uri, rel):
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))

    return path

#generates pdf based on a passed reservation through xhtml2pdf
#the pdf that will be generated will come from an html file populated by the current reservation context
def generatePdf(request, reservation_id):
	reservation = get_object_or_404(Reservation, pk=reservation_id)
	context = {'reservation': reservation}
	html=render_to_string('public_user/book/payment_details_pdf.html', context, request=request)

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=booking_details.pdf'
	
	pdf = pisa.CreatePDF(html, dest=response, link_callback=fetch_resources )
	
	return response


#edits reservation and re-calculates total payment details
@login_required
def editReservation(request, reservation_id):
	reservation = get_object_or_404(Reservation, pk=reservation_id)
	data = dict()
	room_id = request.POST.get('room_id')
	if request.method == 'POST':
		reservation_form = ReservationForm(instance=reservation, initial={'room_id':reservation.room_id.room_type_id})
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		client_email = request.POST.get('client_email')
		client_phone = request.POST.get('client_phone')
		date_out = request.POST.get('date_out')
		date_in = request.POST.get('date_in')
		rooms = Room.objects.filter(room_type_id = room_id)
		days = get_days(date_in,date_out)
		price = get_object_or_404(RoomType, pk=room_id).price
		total_payment = days * price
		available_room = check_availability(rooms,date_in,date_out,reservation_id)
		if available_room:
			reservation.first_name = first_name
			reservation.last_name = last_name
			reservation.client_email =client_email
			reservation.client_phone = client_phone
			reservation.date_in = date_in
			reservation.date_out = date_out
			reservation.room_id = available_room
			reservation.days = days
			reservation.total_payment = total_payment
			reservation.save()

			data['valid_form'] = True
			data['status'] = "created"
			reservations_list = Reservation.objects.all()
			data['reservation_list'] = render_to_string('admin/reservation/view_reservations_list.html', { 'reservations': reservations_list})
		else:
			data['status'] = "invalid"
			data['valid_form'] = False
	else:
		reservation_form = ReservationForm(instance=reservation, initial={'room_id':reservation.room_id.room_type_id})
	context = {'reservation_form': reservation_form}
	data['html_form'] = render_to_string('admin/reservation/edit_reservations.html', context, request=request)
	return JsonResponse(data)

#deletes reservation
@login_required
def deleteReservation(request, reservation_id):
	if request.user.is_authenticated:
		reservation = get_object_or_404(Reservation, pk=reservation_id)
		data = dict()
		if request.method == 'POST':
			reservation.delete()
			reservations_list = Reservation.objects.all()
			data['status'] = "deleted"
			data['reservation_list'] = render_to_string('admin/reservation/view_reservations_list.html', { 'reservations': reservations_list})
		else:
			context= {'reservation': reservation}
			data['status'] = 'none'
			data['html_form'] = render_to_string('admin/reservation/delete_reservation.html', context, request=request)
		return JsonResponse(data)
#handles creation of roomtypes with the option to upload images which is passed through request.FILES
#the image is saved within the project directory and its url is saved in the database
@login_required
def createRoomtype(request):
	data =  dict()
	if request.method == 'POST':
		roomtype_form = RoomTypeForm(request.POST, request.FILES)
		type_name = request.POST.get('type_name')
		price = request.POST.get('price')
		details = request.POST.get('details')
		image = request.FILES.get('image')
		if  not RoomType.objects.filter(type_name=type_name).exists():
			roomtype = RoomType(
				type_name = type_name,
				price = price,
				details = details,
				image =   image
				)
			roomtype.save()
			data['status'] = "created roomtype"
			roomtype_list = RoomType.objects.all()
			data['room_type_list'] = render_to_string('admin/roomtype/view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			data['status'] = "invalid roomtype"
	else:
		roomtype_form = RoomTypeForm()
	context = {'roomtype_form' : roomtype_form}
	data['html_form'] = render_to_string('admin/roomtype/create_roomtype.html', context, request=request)
	return JsonResponse(data)



#edits roomtypes and updates payment details of reservations
@login_required
def editRoomtype(request, room_type_id):
	roomtype = get_object_or_404(RoomType, pk=room_type_id)
	data = dict()
	if request.method == 'POST':
		roomtype_form = RoomTypeForm(instance=roomtype)
		type_name = request.POST.get('type_name')
		price = request.POST.get('price')
		details = request.POST.get('details')
		image =  request.FILES.get('image')
		if not image:
			image = roomtype.image

		if not RoomType.objects.filter(type_name=type_name).exclude(pk=room_type_id).exists():
			select_room  = Room.objects.filter(room_type_id = room_type_id)
			update_reserve = Reservation.objects.filter(room_id__in = select_room)

			for item in update_reserve:
				total = int(item.days) * int(price)
				item.total_payment = total
				item.save()	
			roomtype.type_name = type_name
			roomtype.price = price
			roomtype.details = details
			roomtype.image = image
			roomtype.save()
			data['status'] ="edited roomtype"
			roomtype_list = RoomType.objects.all()
			data['room_type_list'] = render_to_string('admin/roomtype/view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			data['status'] = 'invalid roomtype'

	
	else:
		roomtype_form = RoomTypeForm(instance=roomtype)
	context = {'roomtype_form': roomtype_form}
	data['html_form'] = render_to_string('admin/roomtype/edit_roomtype.html', context, request=request)
	return JsonResponse(data)

#deletes all reservation and rooms that contains a specific roomtype that is being deletd 
@login_required
def deleteRoomtype(request, room_type_id):
	if request.user.is_authenticated:
		roomtype = get_object_or_404(RoomType, pk=room_type_id)
		data = dict()
		if request.method == 'POST':
			roomtype.delete()
			roomtype_list = RoomType.objects.all()
			data['status'] = "deleted roomtype"
			data['roomtype_list'] = render_to_string('admin/roomtype/view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			context= {'roomtype': roomtype}
			data['status'] = 'none'
			data['html_form'] = render_to_string('admin/roomtype/delete_roomtype.html', context, request=request)
		return JsonResponse(data)

#create rooms with unique room numbers
#create rooms based on roomtypes
@login_required
def createRoom(request):
	data =  dict()
	if request.method == 'POST':
		room_form = RoomForm(request.POST)
		room_num = request.POST.get('room_num')
		room_type_id = request.POST.get('room_type_id')
		room_type = get_object_or_404(RoomType, pk=room_type_id)

		if not Room.objects.filter(room_num=room_num).exists():
			room = Room(
				room_num = room_num,
				room_type_id = room_type
				)
			room.save()
			data['status'] = "created room"
			room_list = Room.objects.all()
			data['room_list'] = render_to_string('admin/room/view_room_list.html', { 'rooms': room_list})
		else:
			data['status'] = "invalid room"
	else:
		room_form = RoomForm()
	context = {'room_form' : room_form}
	data['html_form'] = render_to_string('admin/room/create_room.html', context, request=request)
	return JsonResponse(data)

#edit rooms and update payment details of reservations
@login_required
def editRoom(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	data = dict()
	if request.method == 'POST':
		room_form = RoomForm(instance=room)
		room_num = request.POST.get('room_num')
		room_type_id = request.POST.get('room_type_id')

		room_type = get_object_or_404(RoomType, pk=room_type_id)
		if not Room.objects.filter(room_num=room_num).exclude(pk=room_id).exists():	
			
			room.room_num = room_num
			room.room_type_id = room_type
			room.save()
			select_room  = Room.objects.filter(room_type_id = room_type.room_type_id)
			update_reserve = Reservation.objects.filter(room_id__in = select_room)

			for item in update_reserve:
				total = int(item.days) * int(room_type.price)
				item.total_payment = total
				item.save()	
			data['status'] ="edited room"
			room_list = Room.objects.all()
			data['room_list'] = render_to_string('admin/room/view_room_list.html', { 'rooms': room_list})
		else:
			data['status'] = 'invalid room'

	
	else:
		room_form = RoomForm(instance=room)
	context = {'room_form': room_form}
	data['html_form'] = render_to_string('admin/room/edit_room.html', context, request=request)
	return JsonResponse(data)

#also deletes reservations using the room that is being deleted
@login_required
def deleteRoom(request, room_id):
	if request.user.is_authenticated:
		room = get_object_or_404(Room, pk=room_id)
		data = dict()
		if request.method == 'POST':
			room.delete()
			room_list = Room.objects.all()
			data['status'] = "deleted room"
			data['room_list'] = render_to_string('admin/room/view_room_list.html', { 'rooms': room_list})
		else:
			context= {'room': room}
			data['status'] = 'none'
			data['html_form'] = render_to_string('admin/room/delete_room.html', context, request=request)
		return JsonResponse(data)


#required to access admin functions with the 'login_required' tag
#users accessing admin pages without logging-in will be redirected to the login page
def adminLogin(request):
    if request.user.is_authenticated:
        return render(request, 'admin/base/admin_base.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            isValid = "yes"
            return render(request,'admin/base/admin_base.html', {'isValid': isValid})
        else:
            form = AuthenticationForm(request.POST)
            isValid = "no"
            return render(request, 'admin/base/admin_login.html', {'form': form, 'isValid': isValid})
    else:
        form = AuthenticationForm()
        return render(request, 'admin/base/admin_login.html', {'form': form})

#when the user logs-in for the first time, they will be redirected to this page
@login_required
def adminDash(request):
	if request.user.is_authenticated:
		return render(request, 'admin/base/admin_base.html')
#logs-out admin
@login_required
def adminLogout(request):
    logout(request)
    return redirect('/')
#other admin views which requires authentication
@login_required
def reservations(request):
	reservations = Reservation.objects.all()
	return render(request, 'admin/reservation/reservation_list.html', {'reservations':reservations})

@login_required
def roomtypes(request):
	roomtypes = RoomType.objects.all()
	return render(request, 'admin/roomtype/roomtype_list.html', {'roomtypes':roomtypes})
@login_required
def room(request):
	rooms = Room.objects.all()
	return render(request, 'admin/room/room_list.html', {'rooms':rooms})


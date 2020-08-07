from django.shortcuts import render,redirect, get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
import json


def homepage(request):
	return render(request, 'home.html')

# @csrf_exempt
def book(request):
	reservation_form = ReservationForm(request.POST or None)
	room_type = RoomType.objects.all()
	status = ""
	

# 	if request.method == 'POST':
# 		# print(request.POST.get('first_name'))
# 		first_name = request.POST.get('first_name')
# 		last_name = request.POST.get('last_name')
# 		client_email = request.POST.get('client_email')
# 		client_phone = request.POST.get('client_phone')
# 		date_in = request.POST.get('date_in')
# 		date_out = request.POST.get('date_out')
# 		room_id = request.POST.get('room_id')

# 		rooms = Room.objects.filter(room_type_id = room_id)
# 		for room in rooms:
# 			date_out_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_in, date_out__gte=date_in).exists()
# 			date_in_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_out, date_out__gte=date_out).exists()
# 			date_intersect = Reservation.objects.filter(room_id=room, date_in__gte=date_in, date_out__lte=date_out).exists()
# 			# date_intersect = Reservation.objects.filter(room_id=room, date_in__gte=date_in, date_out__lte=date_out).exists()

# 			if not(date_out_intersect or date_in_intersect or date_intersect):
# 				reservation = Reservation(
#             		first_name = first_name,
#             		last_name = last_name,
#             		client_email =client_email,
#             		client_phone = client_phone,
# 	             	date_in = date_in, 
# 	             	date_out = date_out,
# 	             	room_id = room,
# 	             	)
# 				reservation.save()
# 				status = "Room sucessfully booked"
# 				messages.success(request, 'Room sucessfully booked!') 

# 				return render(request, 'book.html', {'reservation_form': reservation_form, 'room_type': room_type})
		
# 		messages.error(request, 'This room is not available on your selected dates!') 
	return render(request, 'book.html', {'reservation_form': reservation_form, 'room_type': room_type })

# @csrf_exempt
def check_availability(rooms, date_in, date_out, reservation_id):
	print(reservation_id)
	for room in rooms:
		date_out_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_in, date_out__gte=date_in).exclude(pk=reservation_id).exists()
		date_in_intersect = Reservation.objects.filter(room_id=room, date_in__lte=date_out, date_out__gte=date_out).exclude(pk=reservation_id).exists()
		date_intersect = Reservation.objects.filter(room_id=room, date_in__gte=date_in, date_out__lte=date_out).exclude(pk=reservation_id).exists()
		# date_intersect = Reservation.objects.filter(room_id=room, date_in__gte=date_in, date_out__lte=date_out).exists()
		if not(date_out_intersect or date_in_intersect or date_intersect):
			return room
	return None
@csrf_exempt
def requestAvailability(request):
	if request.method == 'POST':
		# data = json.loads(request.body)

		date_in = request.POST.get("date_in")
		date_out = request.POST.get("date_out")
		room_id = request.POST.get("room_id")
		rooms = Room.objects.filter(room_type_id = room_id)

		if check_availability(rooms,date_in,date_out):
			response = {'status' : 'available'}
		else:
			response = {'status' : 'unavailable'}
		return JsonResponse(response)

# @csrf_exempt
def createReservation(request):
	if request.method == 'POST':
		# data = json.loads(request.body)
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		client_email = request.POST.get('client_email')
		client_phone = request.POST.get('client_phone')
		date_in = request.POST.get('date_in')
		date_out = request.POST.get('date_out')
		room_id = request.POST.get('room_id')
		rooms = Room.objects.filter(room_type_id = room_id)

		available_room = check_availability(rooms,date_in,date_out,None)

		if available_room:
			reservation = Reservation(
        		first_name = first_name,
        		last_name = last_name,
        		client_email =client_email,
        		client_phone = client_phone,
             	date_in = date_in, 
             	date_out = date_out,
             	room_id = available_room,
             	)
			reservation.save()
			response = {'status' : 'created'}
		else:
			response = {'status' : 'invalid'}
		return JsonResponse(response)



@login_required
def editReservation(request, reservation_id):
	reservation = get_object_or_404(Reservation, pk=reservation_id)
	data = dict()
	if request.method == 'POST':
		reservation_form = ReservationForm(instance=reservation)
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		client_email = request.POST.get('client_email')
		client_phone = request.POST.get('client_phone')
		date_out = request.POST.get('date_out')
		date_in = request.POST.get('date_in')
		room_id = request.POST.get('room_id')
		rooms = Room.objects.filter(room_type_id = room_id)
		available_room = check_availability(rooms,date_in,date_out,reservation_id)
		print(available_room)
		if available_room:
			reservation.first_name = first_name
			reservation.last_name = last_name
			reservation.client_email =client_email
			reservation.client_phone = client_phone
			reservation.date_in = date_in
			reservation.date_out = date_out
			reservation.room_id = available_room
			reservation.save()

			# reservation_form = Reservation(
   #      		first_name = first_name,
   #      		last_name = last_name,
   #      		client_email =client_email,
   #      		client_phone = client_phone,
   #           	date_in = date_in, 
   #           	date_out = date_out,
   #           	room_id = available_room,
   #           	)
			# reservation_form.save()
			data['valid_form'] = True
			data['status'] = "created"
			reservations_list = Reservation.objects.all()
			data['reservation_list'] = render_to_string('view_reservations_list.html', { 'reservations': reservations_list})
		else:
			data['status'] = "invalid"
			data['valid_form'] = False
	else:
		reservation_form = ReservationForm(instance=reservation)
	context = {'reservation_form': reservation_form}
	data['html_form'] = render_to_string('edit_reservations.html', context, request=request)
	return JsonResponse(data)


@login_required
def deleteReservation(request, reservation_id):
	if request.user.is_authenticated:
		reservation = get_object_or_404(Reservation, pk=reservation_id)
		data = dict()
		if request.method == 'POST':
			reservation.delete()
			reservations_list = Reservation.objects.all()
			data['status'] = "deleted"
			data['reservation_list'] = render_to_string('view_reservations_list.html', { 'reservations': reservations_list})
		else:
			context= {'reservation': reservation}
			data['status'] = 'none'
			data['html_form'] = render_to_string('delete_reservation.html', context, request=request)
		return JsonResponse(data)
			
@login_required
def createRoomtype(request):
	data =  dict()
	if request.method == 'POST':
		roomtype_form = RoomTypeForm(request.POST)
		type_name = request.POST.get('type_name')
		if roomtype_form.is_valid() and not RoomType.objects.filter(type_name=type_name).exists():
			print("hi")
			roomtype_form.save()
			data['status'] = "created roomtype"
			roomtype_list = RoomType.objects.all()
			data['room_type_list'] = render_to_string('view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			data['status'] = "invalid roomtype"
	else:
		roomtype_form = RoomTypeForm()
	context = {'roomtype_form' : roomtype_form}
	data['html_form'] = render_to_string('create_roomtype.html', context, request=request)
	return JsonResponse(data)




@login_required
def editRoomtype(request, room_type_id):
	roomtype = get_object_or_404(RoomType, pk=room_type_id)
	print(roomtype)
	data = dict()
	if request.method == 'POST':
		roomtype_form = RoomTypeForm(instance=roomtype)
		type_name = request.POST.get('type_name')
		price = request.POST.get('price')
		if not RoomType.objects.filter(type_name=type_name).exclude(pk=room_type_id).exists():	
			roomtype.type_name = type_name
			roomtype.price = price
			roomtype.save()
			data['status'] ="edited roomtype"
			roomtype_list = RoomType.objects.all()
			print(data['status'])
			data['room_type_list'] = render_to_string('view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			data['status'] = 'invalid roomtype'

	
	else:
		roomtype_form = RoomTypeForm(instance=roomtype)
	context = {'roomtype_form': roomtype_form}
	data['html_form'] = render_to_string('edit_roomtype.html', context, request=request)
	return JsonResponse(data)


@login_required
def deleteRoomtype(request, room_type_id):
	if request.user.is_authenticated:
		roomtype = get_object_or_404(RoomType, pk=room_type_id)
		data = dict()
		if request.method == 'POST':
			roomtype.delete()
			roomtype_list = RoomType.objects.all()
			data['status'] = "deleted roomtype"
			data['roomtype_list'] = render_to_string('view_roomtype_list.html', { 'roomtypes': roomtype_list})
		else:
			context= {'roomtype': roomtype}
			data['status'] = 'none'
			data['html_form'] = render_to_string('delete_roomtype.html', context, request=request)
		return JsonResponse(data)





def adminLogin(request):
    if request.user.is_authenticated:
        return render(request, 'admin_dash.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request,'admin_dash.html')
        else:
            form = AuthenticationForm(request.POST)
            return render(request, 'admin_login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'admin_login.html', {'form': form})

@login_required
def adminDash(request):
	if request.user.is_authenticated:
		return render(request, 'admin_dash.html')

def adminLogout(request):
    logout(request)
    return redirect('/')

@login_required
def reservations(request):
	reservations = Reservation.objects.all()
	return render(request, 'reservation_list.html', {'reservations':reservations})

@login_required
def roomtypes(request):
	roomtypes = RoomType.objects.all()
	return render(request, 'roomtype_list.html', {'roomtypes':roomtypes})




# Create your views here.

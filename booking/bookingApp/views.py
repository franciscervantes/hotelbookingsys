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


def homepage(request):
	roomtypes = RoomType.objects.all()
	return render(request, 'home.html', {'roomtypes':roomtypes})

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
def get_days(date_in, date_out):
	date_format = "%Y-%m-%d"
	a = datetime.strptime(date_in, date_format)
	b = datetime.strptime(date_out, date_format)
	delta = b - a
	return delta.days 

def createReservation(request):
	if request.method == 'POST':
		# data = json.loads(request.body)
		data = dict()
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		client_email = request.POST.get('client_email')
		client_phone = request.POST.get('client_phone')
		date_in = request.POST.get('date_in')
		date_out = request.POST.get('date_out')
		room_id = request.POST.get('room_id')
		rooms = Room.objects.filter(room_type_id = room_id)
		print(rooms)
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
			data['html_form'] = render_to_string('payment_details.html', context, request=request)
			html=render_to_string('payment_details.html', context, request=request)
			
		else:
			if rooms:
				roomExists = True
			else:
				roomExists = False

			context = {'reservation': reservation, 'roomExists':roomExists}
			data['html_form'] = render_to_string('booking_error.html',context, request=request)
			data['status'] = 'invalid'
		return JsonResponse(data)

def fetch_resources(uri, rel):
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    print(path)

    return path


def generatePdf(request, reservation_id):
	reservation = get_object_or_404(Reservation, pk=reservation_id)
	context = {'reservation': reservation}
	html=render_to_string('payment_details_pdf.html', context, request=request)
	# file = open('test.pdf', "w+b")
	# pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,encoding='utf-8',link_callback=fetch_resources)
	# file.seek(0)
	# pdf = file.read()
	# file.close()
	# return HttpResponse(pdf, 'application/pdf')

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=booking_details.pdf'
	
	pdf = pisa.CreatePDF(html, dest=response, link_callback=fetch_resources )
	

	
	return response
	# return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))


# def generatePdf(request, reservation_id):
# 	reservation = get_object_or_404(Reservation, pk=reservation_id)
# 	context = {'reservation': reservation}
# 	html=render_to_string('payment_details.html', context, request=request)
# 	fid, fname = mkstemp(dir='/tmp')
# 	f = open(fname, 'w+b')
# 	f.write(html)
# 	f.close()
# 	cmd = 'xhtml2pdf "%s"' % fname
# 	os.system(cmd)
# 	os.unlink(fname)
# 	filename = fname+'.pdf'
# 	pdf = open(filename, 'r')
# 	content = pdf.read()
# 	pdf.close()
# 	os.unlink(pdf.name)
# 	response = HttpResponse(content, mimetype='application/pdf')
# 	response['Content-Disposition'] = 'attachment; filename=draft.pdf'


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
		days = get_days(date_in,date_out)
		price = get_object_or_404(RoomType, pk=room_id).price
		total_payment = days * price
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
			reservation.days = days
			reservation.total_payment = total_payment
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
		roomtype_form = RoomTypeForm(request.POST, request.FILES)
		type_name = request.POST.get('type_name')
		price = request.POST.get('price')
		details = request.POST.get('details')
		image = request.FILES.get('image')
		if  not RoomType.objects.filter(type_name=type_name).exists():
			print("hi")
			roomtype = RoomType(
				type_name = type_name,
				price = price,
				details = details,
				image =   image
				)
			roomtype.save()
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
		details = request.POST.get('details')
		image =  request.FILES.get('image')
		if not image:
			image = roomtype.image

		if not RoomType.objects.filter(type_name=type_name).exclude(pk=room_type_id).exists():	
			roomtype.type_name = type_name
			roomtype.price = price
			roomtype.details = details
			roomtype.image = image
			roomtype.save()
			data['status'] ="edited roomtype"
			roomtype_list = RoomType.objects.all()
			print(data['status'])
			# data['image_url'] = roomtype.image.url
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

@login_required
def createRoom(request):
	data =  dict()
	if request.method == 'POST':
		room_form = RoomForm(request.POST)
		room_num = request.POST.get('room_num')
		room_type_id = request.POST.get('room_type_id')
		# room_type = RoomType.objects.filter(pk=room_type_id)
		room_type = get_object_or_404(RoomType, pk=room_type_id)

		if not Room.objects.filter(room_num=room_num).exists():
			print("helO")
			room = Room(
				room_num = room_num,
				room_type_id = room_type
				)
			room.save()
			data['status'] = "created room"
			room_list = Room.objects.all()
			data['room_list'] = render_to_string('view_room_list.html', { 'rooms': room_list})
		else:
			data['status'] = "invalid room"
	else:
		room_form = RoomForm()
	context = {'room_form' : room_form}
	data['html_form'] = render_to_string('create_room.html', context, request=request)
	return JsonResponse(data)

@login_required
def editRoom(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	data = dict()
	if request.method == 'POST':
		room_form = RoomForm(instance=room)
		room_num = request.POST.get('room_num')
		room_type_id = request.POST.get('room_type_id')

		room_type = get_object_or_404(RoomType, pk=room_type_id)
		print(room_type)
		if not Room.objects.filter(room_num=room_num).exclude(pk=room_id).exists():	
			room.room_num = room_num
			room.room_type_id = room_type
			room.save()
			data['status'] ="edited room"
			room_list = Room.objects.all()
			data['room_list'] = render_to_string('view_room_list.html', { 'rooms': room_list})
		else:
			data['status'] = 'invalid room'

	
	else:
		room_form = RoomForm(instance=room)
	context = {'room_form': room_form}
	data['html_form'] = render_to_string('edit_room.html', context, request=request)
	return JsonResponse(data)

@login_required
def deleteRoom(request, room_id):
	if request.user.is_authenticated:
		room = get_object_or_404(Room, pk=room_id)
		data = dict()
		if request.method == 'POST':
			room.delete()
			room_list = Room.objects.all()
			data['status'] = "deleted room"
			data['room_list'] = render_to_string('view_room_list.html', { 'rooms': room_list})
		else:
			context= {'room': room}
			data['status'] = 'none'
			data['html_form'] = render_to_string('delete_room.html', context, request=request)
		return JsonResponse(data)





def adminLogin(request):
    if request.user.is_authenticated:
        return render(request, 'admin_base.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            isValid = "yes"
            return render(request,'admin_base.html', {'isValid': isValid})
        else:
            form = AuthenticationForm(request.POST)
            isValid = "no"
            return render(request, 'admin_login.html', {'form': form, 'isValid': isValid})
    else:
        form = AuthenticationForm()
        return render(request, 'admin_login.html', {'form': form})

@login_required
def adminDash(request):
	if request.user.is_authenticated:
		return render(request, 'admin_base.html')

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
@login_required
def room(request):
	rooms = Room.objects.all()
	return render(request, 'room_list.html', {'rooms':rooms})




# Create your views here.

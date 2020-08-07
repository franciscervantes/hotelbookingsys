from django import forms
from .models import *
class DateInput(forms.DateInput):
    input_type = 'date'

class ReservationForm(forms.ModelForm):
	
	first_name = forms.CharField(label='First name', max_length=128)
	last_name =  forms.CharField(label='Last name', max_length=128)
	client_email = forms.CharField(label='Email', max_length=128)
	client_phone = forms.CharField(label='Phone', max_length=128)
	room_id = forms.ModelChoiceField(queryset=RoomType.objects.all() ,initial=0, label="Room Type", widget=forms.Select(attrs={"onChange":'showRoom(this.value)'}))
	date_in = forms.DateField(widget=forms.TextInput(
		attrs={'class':'datepicker', 'id': 'datein'}) ,input_formats=['%Y-%m-%d'])
	date_out = forms.DateField(widget=forms.TextInput(
			attrs={'class':'datepicker', 'id':'dateout'}),input_formats=['%Y-%m-%d'])

	class Meta:
		model = Reservation
		fields=['first_name', 'last_name', 'client_email', 'client_phone', 'room_id', 'date_in', 'date_out']


class RoomTypeForm(forms.ModelForm):
	class Meta:
		model = RoomType
		fields = '__all__'






# user = User.objects.create_user(username='admin1234', password='admin')


    



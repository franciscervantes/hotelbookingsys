# hotelbookingsys

This is a hotel booking system where the CRUD API was developed through Python and Django. The requests are sent through AJAX calls from the frontend.

![alt text](https://user-images.githubusercontent.com/30710843/94362418-b80c6000-00ed-11eb-9f51-9496c558587e.png)

## Installation

Create virtual environment

```bash
virtualenv venv
venv/Scripts/activate

```
Install dependencies

```bash
cd booking
pip install -r requirements.txt

```
Install [mysql](https://dev.mysql.com/downloads/installer/) then change mysql password in booking/booking/settings.py file

Run MySQL Command Line Client
```bash
CREATE DATABASE bookingapp;

```
Run database migrations
```bash
python manage.py migrate
```
Run server

```bash
python manage.py runserver
```
## Usage

Admin credentials

```bash
username: admin1234
password: admin
```
Note: Room types and rooms should be added first in the admin section of the app before creating/booking reservations.
*Admin login page could be accessed in the top-right corner of the application*

## Features

- Reservation
  - View All Reservations
  - Edit Reservations
  - Delete Reservations
  - Search Reservations
- Room Types
  - View All Room Types
  - Edit Room Types
  - Delete Room Types
  - Search Room Types
  - Create Room Types
  - Upload Room Type Images
- Rooms
  - View All Rooms
  - Edit Rooms
  - Delete Rooms
  - Search Rooms
  - Create Rooms
  
- Booking
  - Create Booking
  - View Available Rooms

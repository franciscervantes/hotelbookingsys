# hotelbookingsys

## Installation

Create virtual environment

```bash
virtualenv venv
venv/Scripts/activate

```
Install dependencies

```bash
pip install -r requirements.txt

```
Install [mysql](https://dev.mysql.com/downloads/installer/) then change mysql password in booking/booking/settings.py file

Run MySQL Command Line Client
```bash
CREATE DATABASE bookingapp;

```
Run database migrations
```bash
cd booking
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
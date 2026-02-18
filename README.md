# Water It - Flask Edition

A responsive web adaptation of the original Water It Flutter application.  
Built with Flask while preserving the original design system and UI philosophy.

------------------------------------------------------------

## Overview

Water It Web is a fully responsive browser-based version of the original Flutter mobile application.

This project maintains:

- Clean architecture structure
- Plant management system (CRUD)
- Weather integration (OpenWeather API)
- Reminders system
- Push notifications
- Modern soft UI design
- Mobile-first responsive layout

------------------------------------------------------------

## Screenshots

<p align="center">
  <img src="screenshots/4.png" width="250"/>
  <img src="screenshots/2.png" width="250"/>
  <img src="screenshots/3.png" width="250"/>
</p>


------------------------------------------------------------

## Architecture

Backend:
- Flask
- SQLite
- APScheduler (background reminders)
- Web Push Notifications
- OpenWeather API
- Blueprint-based modular structure

Frontend:
- Custom CSS Design System
- Mobile-first responsive layout
- Reusable UI components
- Bottom navigation system

------------------------------------------------------------

## 🔗 Original Flutter Project

This web version is inspired by and adapted from the original Flutter project.

Original Flutter Design & Application by:

kingdrofd

Repository:
https://github.com/kingdrofd/water_it

All design credits belong to the original creator.

------------------------------------------------------------

## Installation

git clone https://github.com/yahiawork/Water-it-Flask-Edition-.git
```
cd Water-it-Flask-Edition-
```
```
python -m venv venv
```
Windows:
```
venv\Scripts\activate
```
Linux / macOS:
```
source venv/bin/activate
```
```
pip install -r requirements.txt
python run.py
```
Open in browser:
```
http://127.0.0.1:5000
```
------------------------------------------------------------

## Weather API Setup

 - Create a .env file in the root directory:
```
OPENWEATHER_API_KEY=your_api_key_here
DEFAULT_CITY=Fes
```
Get a free API key from:
https://openweathermap.org/

------------------------------------------------------------

## Features

- Full plant CRUD system
- Multiple image upload
- Weather forecast integration
- Reminder scheduling
- Push notifications
- SQLite persistence
- Fully responsive UI
- Clean structured backend

------------------------------------------------------------

## Responsive Design

The layout adapts to:

- Mobile phones
- Tablets
- Desktop screens

Designed to preserve the original mobile app feel inside a web environment.

------------------------------------------------------------

## Credits

Original Flutter design and concept:

kingdrofd
https://github.com/kingdrofd/water_it


Web adaptation and backend implementation:
Yahia Saad / yahiawork

------------------------------------------------------------

## License

MIT License

This web adaptation is based on the original Flutter design created by kingdrofd.
All design credits belong to the original author.

The software is provided "as is", without warranty of any kind.

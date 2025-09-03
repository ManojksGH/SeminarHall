#  Seminar Hall Booking System

A **Django-based web application** for managing and booking seminar halls efficiently.  
This project allows users to register, book halls, upload hall images, and manage booking statuses with an easy-to-use dashboard.

 Features
- User authentication (login, register, change password)
- Book seminar halls with real-time status checking
- Upload and manage hall images
- Separate dashboards for **Admins** and **Users**
- Email notifications for booking confirmation
- Secure session management (auto logout after inactivity)
- Responsive frontend templates with static assets


Project Structure
Seminarhall/
├── dbms/ # Django project folder
│ ├── dbms/ # Project settings and configs
│ │ ├── settings.py
│ │ ├── urls.py
│ │ ├── wsgi.py
│ │ └── asgi.py
│ ├── seminar/ # Core app (models, views, forms, templates)
│ │ ├── migrations/
│ │ ├── static/ # CSS/JS/images
│ │ ├── templates/ # HTML templates
│ │ ├── admin.py
│ │ ├── models.py
│ │ ├── urls.py
│ │ └── views.py
│ ├── manage.py
│ └── db.sqlite3 # Local development DB
├── media/ # Uploaded hall images
├── README.md
├── LICENSE
└── .gitignore

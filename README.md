# Online Doctor Appointment Booking System (ODABS)

ODABS (Online Doctor Appointment Booking System) is a web-based application for booking and managing doctor appointments.

Patients can search for doctors, view doctor information and availability, book appointments, and manage their appointments. Doctors can manage appointments and schedules, while administrators manage doctors, hospitals, and other system data.

The application is built with Django and PostgreSQL. The project also applies DevOps practices including Docker, Docker Compose, GitHub Actions, Docker Hub, and Kubernetes.

---

## Tech Stack

### Application
- Python
- Django
- PostgreSQL
- HTML
- CSS
- JavaScript

### DevOps
- Git
- GitHub
- Docker
- Docker Compose
- GitHub Actions
- Docker Hub
- Kubernetes
- Minikube
- NGINX Ingress

---

## Project Architecture

```mermaid
flowchart TD
    A[Developer] --> B[GitHub]

    B --> C[GitHub Actions]
    C --> D[Django Checks]
    C --> E[Database Migration]
    C --> F[Build Docker Image]

    F --> G[Docker Hub]
    G --> H[Kubernetes]

    H --> I[ODABS Deployment]
    I --> J[ODABS Pods]
    J --> K[ODABS Service]
    K --> L[NGINX Ingress]
    L --> M[User]

    J --> N[PostgreSQL Service]
    N --> O[PostgreSQL Pod]
    O --> P[Persistent Storage]





















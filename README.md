# BuyTheWay
BuyTheWay is created by the group, SanaHaul. As a project to centralize and secure the pasabuy experience in the Philippines.

## 👥 Group Members
1. Alinus Abuke
2. Hanzo Castillo
3. Paige Carbonell
4. Lance De Guzman
5. Kimberly Sioco

## 📋 Project Overview

The objectives of the project are the following:
1. To create centralized website for the Pasabuy community
2. To allow communication between Sellers and Buyers

## 🛠 Tech Stack

* **Language:** Python 3.13
* **Backend Framework:** Django 6.0
* **Frontend Framework:** Vue.js
* **Deployment:** PythonAnywhere

---

## ⚙️ Configuration & Security

### Environment Variables

1.  Create a `.env` file in the root directory (same level as `manage.py` and `Dockerfile`).

## 🚀 Installation & Running

You can run the application using **Python**.

### Prerequisites
* [Git](https://git-scm.com/)
* [Python 3.13+](https://www.python.org/) (for Manual method)

### 1. Clone the Repository
```bash
git clone https://github.com/lancedguzman/BuyTheWay.git
```

### 2. Configure Environment Variables
Create your own .env from the given example
```bash
# Linux/Mac
cd BuyTheWay
cp .env.example .env
```

```bash
# Windows
cd BuyTheWay
copy .env.example .env
```

### 3. Create Python Virtual Environment
```bash
# Windows
python -m venv venv
```

```bash
# Linux/Mac
python3 -m venv venv
```

### 4. Download Requirements.txt
```bash
pip install -r requirements.txt
```

### 5. Create Migrations and Migrate
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run Server
```bash
python manage.py runserver
```

## 🧪 Running Tests
To run the Unit Cases
```bash
# Via Python
python manage.py test
```

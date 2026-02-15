# BuyTheWay
BuyTheWay is created by the group, SanaHaul. As a project to centralize and secure the pasabuy experience in the Philippines.

## 📋 Project Overview

The objectives go here.

## 🛠 Tech Stack

* **Language:** Python 3.13
* **Backend Framework:** Django 6.0
* **Frontend Framework:** Vue.js
* **Containerization:** Docker & Docker Compose
* **Deployment:** PythonAnywhere

---

## ⚙️ Configuration & Security

### Environment Variables

1.  Create a `.env` file in the root directory (same level as `manage.py` and `Dockerfile`).

## 🚀 Installation & Running

You can run the application using **Docker** or **Manually**.

### Prerequisites
* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Docker method)
* [Python 3.13+](https://www.python.org/) (for Manual method)

### 1. Clone the Repository
```bash
git clone [https://github.com/lancedguzman/heal.ai.git](https://github.com/lancedguzman/BuyTheWay.git)
cd BuyTheWay
```

### 2. Configure Environment Variables
Create your own .env from the given example
```bash
# Linux/Mac
cp .env.example .env
```

```bash
# Windows
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

### 5. Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run Server
```bash
python manage.py runserver
```

## 7. Docker Setup
```bash
docker-compose up --build
```

## 🧪 Running Tests
To run the Rest API test
```bash
# Via Docker
docker-compose run web python manage.py test
```

```bash
# Via Python
python manage.py test
```

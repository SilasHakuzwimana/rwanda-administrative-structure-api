# 🇷🇼 Rwanda Administrative Structure API

This project provides a RESTful API for accessing Rwanda's administrative divisions — from provinces down to villages — using Django and Django REST Framework.

## 📌 Overview

This API enables consumers to programmatically access and manage Rwanda’s hierarchical administrative units, structured as:

- **Province**
- **District**
- **Sector**
- **Cell**
- **Village**

Each unit is linked to its parent through foreign keys, maintaining a clean and scalable data structure.

## 🚀 Features

- RESTful endpoints for CRUD operations on each administrative level
- Nested structure through foreign key relationships
- Easily extensible and scalable
- Built with Django and Django REST Framework
- Ready for production deployment or integration with external systems

## 🧱 Tech Stack

- Python 3.10+
- Django 4.x
- Django REST Framework
- SQLite (default) or switchable to PostgreSQL/MySQL
- Optional: Docker support (can be added later)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/SilasHakuzwimana/rwanda-administrative-structure-api.git
cd rwanda-administrative-structure-api
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Development Server

```bash
python manage.py runserver
```

### 6. Access the API

Base URL: `http://127.0.0.1:8000/api/`

| Endpoint            | Description      |
| ------------------- | ---------------- |
| `/api/provinces/` | Manage provinces |
| `/api/districts/` | Manage districts |
| `/api/sectors/`   | Manage sectors   |
| `/api/cells/`     | Manage cells     |
| `/api/villages/`  | Manage villages  |

---

## 🗃️ API Models Structure

Each model is structured hierarchically:

* `District` → belongs to `Province`
* `Sector` → belongs to `District`
* `Cell` → belongs to `Sector`
* `Village` → belongs to `Cell`

---

## 🔐 Authentication

> No authentication is required by default. Add token-based or session-based authentication as needed using DRF settings.

---

## 🧪 Testing the API

You can use tools like:

* [Postman](https://www.postman.com/)
* [Insomnia](https://insomnia.rest/)
* CURL (`curl http://localhost:8000/api/provinces/`)

---

## 📦 Future Improvements

* Add filtering and search capabilities (e.g., filter districts by province)
* Enable nested endpoints (e.g., `/provinces/{id}/districts/`)
* Connect to a real source of Rwanda’s administrative data
* Add Swagger/OpenAPI documentation
* Add Docker support for containerized deployment

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Maintainer

**Silas HAKUZWIMANA**
**Phone: +250 783 749 019**
DevOps Engineer & Full Stack Developer
📧 [hakuzwisilas@gmail.com](mailto:hakuzwisilas@gmail.com)
🌐 [LinkedIn](https://linkedin.com/in/SilasHakuzwimana)

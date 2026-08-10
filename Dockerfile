FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--workers=4", "--threads=2", "--bind=0.0.0.0:8000", "rwanda_admin_api.wsgi:application"]
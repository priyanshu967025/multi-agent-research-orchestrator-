web: cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn orchestrator_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120

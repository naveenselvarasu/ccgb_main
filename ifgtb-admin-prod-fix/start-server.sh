#!/usr/bin/env bash
# start-server.sh
#if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
#    (cd pincode-admin; python manage.py createsuperuser --no-input)
#fi
(python jamun-admin/manage.py collectstatic --noinput; cd jamun-admin; gunicorn jamun_admin.wsgi --user www-data --bind 0.0.0.0:8000 --workers 3 --error-logfile /opt/jamun_assets/logs/gunicorn/error.log --access-logfile /opt/jamun_assets/logs/gunicorn/access.log --log-level=INFO;)
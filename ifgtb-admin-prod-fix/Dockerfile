
# pull official base image
FROM python:3.9

# set work directory
WORKDIR /treegenie_admin

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
#RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

#EXPOSE 8000

CMD ["python manage.py migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
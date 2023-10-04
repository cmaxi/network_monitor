#Deriving the latest base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN pip install --upgrade pip
RUN pip install setuptools

RUN apt-get update -y

    
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src

# pull official base image
FROM python:3.9.7-alpine

# set work directory
WORKDIR /usr/src/long_polling_api

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy code
COPY . .

# run bot
CMD ["python", "main.py"]
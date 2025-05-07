FROM python:alpine3.20

ENV PYTHONUNBUFFERED 1

RUN apk update && apk add nano

WORKDIR /app

COPY ./ ./

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

EXPOSE 8000
 
CMD ["gunicorn", "-c", "config/gunicorn/conf.py","--bin",":8000","--chdir","backend","backend.wsgi:application"]
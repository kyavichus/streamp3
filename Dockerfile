FROM python:3.9
LABEL AUTHOR = kyavichus

WORKDIR /app
COPY lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages 
COPY . .

EXPOSE 12345

CMD ["python", "-u", "server.py"]

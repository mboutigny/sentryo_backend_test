FROM python:3.4-alpine
RUN mkdir -p /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]


FROM python:3.7
COPY . /backend
WORKDIR /backend

EXPOSE 5000
RUN pip install -r requirements.txt

CMD python -u app.py

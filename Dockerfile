FROM python:3.10.9

WORKDIR /home/host

COPY . .

RUN pip install -r requirements.txt

CMD python main.py
FROM python:3.8.10-slim

WORKDIR /home/task

COPY . ./

RUN pip install -r requirements.txt

CMD (cd src/ && python3 application.py &) && (python3 checker.py host.docker.internal 8080 check)
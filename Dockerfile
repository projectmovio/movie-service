FROM python:3.7-alpine3.8

EXPOSE 8082

ADD . "/usr/local/src"
WORKDIR "/usr/local/src"

RUN pip install -r requirements.txt
CMD ["python", "run_flask.py"]

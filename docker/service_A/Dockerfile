

FROM python:3.12-slim

WORKDIR /app

COPY requarment_base.txt .

COPY /docker/service_A/service_A_req.txt .

RUN pip install -r service_A_req.txt

COPY . .

ENV PYTHONPATH=/app

CMD [ "python" , "docker/service_A/service_A_deploy.py"]



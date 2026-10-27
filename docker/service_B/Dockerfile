

FROM python:3.12-slim

WORKDIR /app

COPY requarment_base.txt .

COPY /docker/service_B/service_b_req.txt .

RUN pip install -r service_b_req.txt

COPY . .

ENV PYTHONPATH=/app

CMD [ "python" , "docker/service_B/service_b_deploy.py"]



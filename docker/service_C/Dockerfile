

FROM python:3.12-slim

WORKDIR /app

COPY requarment_base.txt .

COPY /docker/service_C/service_c_req.txt .

RUN pip install -r service_c_req.txt

COPY . .

ENV PYTHONPATH=/app

CMD [ "python" , "docker/service_C/service_c_deploy.py"]



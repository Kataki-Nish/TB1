
FROM python:3.12-slim

WORKDIR /app

COPY requarment_base.txt .

COPY /docker/requester/requester_req.txt .

RUN pip install -r requester_req.txt

COPY . .

ENV PYTHONPATH=/app

CMD [ "python" , "docker/requester/requester_deploy.py" ]




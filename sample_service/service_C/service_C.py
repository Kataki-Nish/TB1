

from sample_service.service import Service
from proto import host_and_port





service_C = Service(service_name="C",port=host_and_port.service_C.port,host=host_and_port.service_C.host)


@service_C.app.get("/number")
def get_number():

    return 3


@service_C.app.get("/string")
def get_str():

    return "Hello"




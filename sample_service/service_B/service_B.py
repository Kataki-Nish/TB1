


from sample_service.service import Service
from proto import host_and_port






service_B = Service(service_name="B",port=host_and_port.service_B.port,host=host_and_port.service_B.host)


@service_B.app.get("/number")
def get_number():

    return 5










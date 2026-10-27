

from sample_service.service import Service , return_response
from SDK import sdk_v4
from proto import host_and_port
from proto.starters import starters
import httpx



service_A = Service("A",port=host_and_port.service_A.port,host=host_and_port.service_A.host)

@service_A.app.get("/check")
def check():

    return {"status":"OK"}

@service_A.app.get("/call_B")
def call_B():

    try:

        b = service_A.client.get(f"http://{host_and_port.service_B.host}:{host_and_port.service_B.port}/number")

        b = return_response(b)

        return {"call_B":b}

    except httpx.ConnectError:

        print("server of service B is disconect yet .")

@service_A.app.get("/call_C1")
def call_C1():

    try:

        c1 = service_A.client.get(f"http://{host_and_port.service_C.host}:{host_and_port.service_C.port}/number")

        c1 = return_response(c1)

        return {"call_C1":c1}

    except httpx.ConnectError:

        print("server of service C is disconect yet .")


@service_A.app.get("/call_C2")
def call_C1():

    try:

        c2 = service_A.client.get(f"http://{host_and_port.service_C.host}:{host_and_port.service_C.port}/string")

        c2 = return_response(c2)

        return {"call_C2":c2}

    except httpx.ConnectError:

        print("server of service C is disconect yet .")




sdk = sdk_v4.Sdk(service_app=service_A.app)

sdk.setup()





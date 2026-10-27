

from dataclasses import dataclass


@dataclass
class Protocol_data:
    component: str
    host: str
    port: int



service_A = Protocol_data(component="service_A",host="service_a",port=8000)

service_B = Protocol_data(component="service_B",host="service_b",port=8001)

service_C = Protocol_data(component="service_C",host="service_c",port=8002)

agent_SDK_client = Protocol_data(component="agent",host="sdk_client",port=5000)

SDK_agent_client = Protocol_data(component="SDK",host="agent_client",port=6000)







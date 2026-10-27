

from dataclasses import dataclass

from typing import Optional , TypedDict



y : list[int] = []

x : dict[str,int] = {}

aggregator_schema = {
    "timestamp": None,

    "RED_metrics": {
        "inbound": {
            "window": int,
            "request_count": int,
            "error_count": int,
            "latency_histogram": str,
        },
        "outbound" : {#Dict[key=dependency_name , value=things in the {}]
            "dependency_name" : {
            "window" : int,
            "request_count" : int ,
            "error_count" : int,
            "latency_histogram" : str
            }
        }
    },

    "USE_metrics": {
        "cpu": {
            "cpu_utilization": float,
            "cpu_cores": float,
        },

        "memory": {
            "avg_memory_utilization": float,
            "max_memory_utilization": float,
        },

        "disk": {
            "read_bytes": int,
            "write_bytes": int,
            "io_bytes": int,
        },

        "network": {
            "rx_bytes": int,
            "tx_bytes": int,
        }
    }
}


agent_state_report_shema = {
    "timestamp": int ,
    "window": 10 , #(sec)
    "service_name": str ,
    "instance_id": int ,
    "agregater_output" : aggregator_schema
}



# --------



class Heartbeat:
    def __init__(
        self,
        timestamp: int,
        component_type: str,
        component_id: int
    ):
        self.timestamp = timestamp
        self.component_type = component_type
        self.component_id = component_id

# == 

@dataclass
class Heartbeat:
    timestamp: int
    component_type: str
    component_id: int




# --------


#proto


@dataclass
class Dependency_name:
    window : int
    request_count : int
    error_count : int
    latency_histogram : str


@dataclass
class Inbound:
    window : int
    request_count : int
    error_count : int
    latency_histogram : str



@dataclass
class Outbound:
    dependency_name : Dependency_name




@dataclass
class RED_metrics:
    inbound : Inbound
    outbound : Outbound
    





@dataclass
class CPU:
    cpu_utilization : float
    cpu_cores : float




@dataclass
class Memory:
    avg_memory_utilization : float
    max_memory_utilization : float



@dataclass
class Disk:
    read_bytes : int
    write_bytes : int
    io_bytes : int



@dataclass
class Network:
    rx_bytes : int
    tx_bytes : int




@dataclass
class USE_metrics:
    cpu : CPU
    memory : Memory
    disk : Disk
    network : Network




@dataclass
class Aggregator_schema:
    timestamp : int
    red_metrics : RED_metrics
    use_metrics : USE_metrics



@dataclass
class Agent_state_report_shema:
    timestamp : int
    window : int
    service_name : str
    instance_id : int
    agregater_shema : Aggregator_schema


#example
a = Agent_state_report_shema(timestamp=2,window=3,service_name="str",instance_id=3,agregater_shema=Aggregator_schema())




# ------



@dataclass
class Problem_state:
    reason : str
    code : int | None
    number : Optional[float]




# NOT used in TB1
class HeartbeatDict(TypedDict): #class variable
    timestamp: int
    component_type: str
    component_id: int




@dataclass
class Heartbeat: #instance variable
    timestamp: int
    component_type: str
    component_id: int



h1 = HeartbeatDict() # wrong use

h2 : HeartbeatDict = {"timestamp":2,"component_type":"asd","component_id":12} # right use

h3 = Heartbeat()





"""


Dataclass
↓
dict
↓
JSON
↓
UDS/gRPC (SDK ↔ Agent)

Dataclass
↓
dict
↓
JSON
↓
TCP/gRPC (Agent ↔ Control Plane | SDK ↔ Control Plane)





Heartbeat Dataclass
↓
asdict()
↓
dict
↓
json.dumps()
↓
JSON string
↓
Transport
↓
JSON string
↓
json.loads()
↓
dict
↓
Heartbeat(**dict)
↓
Heartbeat Dataclass




Example:


Dataclass
1.    ↓
dict
2.    ↓
JSON / Protobuf
3.    ↓
transport
4.    ↓
JSON / Protobuf
5.    ↓
dict
6.    ↓
Dataclass


from dataclasses import asdict

h = Heartbeat(
    timestamp=123,
    component_type="SDK",
    component_id=1,
)

#1.Dataclass -> dict
payload = asdict(h)


import json

#2.dict -> JSON
raw = json.dumps(payload)


3.JSON -> transport
Transport Layer



4.transport -> JSON
Transport Layer



5.JSON -> dict
data = json.loads(raw)


6.dict -> Dataclass
h = Heartbeat(**data)



"""






#shema

@dataclass
class Raw_shema:
    timestamp : int
    service_name : str
    instance_id : int
    red_metrics : RED_metrics
    use_metrics : USE_metrics

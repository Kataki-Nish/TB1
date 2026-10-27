

from dataclasses import dataclass

from typing import List







@dataclass
class RED:
    window : float
    request_count : int
    error_count : int
    latency_histogram : dict



@dataclass
class Inbound:
    red : RED


@dataclass
class Outbound:
    dependency_name : str
    red : RED






@dataclass
class RED_metrics:
    inbound : Inbound
    outbounds : List[Outbound]
    



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
    red_metrics : RED_metrics | None
    use_metrics : USE_metrics | None



@dataclass
class Agent_state_report_shema:
    timestamp : float
    window : float
    service_name : str
    instance_id : int
    agregater_shema : Aggregator_schema







@dataclass
class SDK_reprot_shema:
    timestamp : float
    service_name : str
    instance_id : int
    bound_type : Inbound | Outbound





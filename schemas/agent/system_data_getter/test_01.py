

from dataclasses import dataclass



@dataclass
class Target_selector_rules:
    service_name: str



@dataclass
class Execution_env_metadata:
    orchestrator: str
    container_runtime: str
    cgroup_driver: str
    cgroup_version: str
    host_environment: str


@dataclass
class Target_container_identity:
    container_id: str




@dataclass
class PID_discovery_output:
    runtime_pid: str
    host_PID: str




@dataclass
class Workload_resolver_output:
    runtime_pid: str
    host_PID: str
    cgroup_absolute_path: str
    namespace_handler_path: str



@dataclass
class Env_datas:
    execution_env_metadatas: Execution_env_metadata
    target_container_identity: Target_container_identity


@dataclass
class Discoverer_results:
    host_PID: str
    cgroup_absolute_path: str
    namespace_handler_path: str
    cgroup_version: str


@dataclass
class Identity_datas:
    runtime_pid: str
    container_starttime: str


@dataclass
class Discoverer_output:
    env_datas: Env_datas
    discoverer_results: Discoverer_results
    identity_datas: Identity_datas





@dataclass
class Disk_utilization:
    read_bytes: int
    write_bytes: int
    io_bytes: int




@dataclass
class Network_utilization:
    rx_bytes: int
    tx_bytes: int





@dataclass
class Metric_10s:
    timestamp: float
    s_time: float
    CLK_TCK: int
    effective_cpu_count: float
    cpu_time: float
    max_memory: int
    read_bytes: int
    write_bytes: int
    io_bytes: int
    rx_bytes: int
    tx_bytes: int





@dataclass
class Metric_500ms:
    timestamp: float
    current_memory: int




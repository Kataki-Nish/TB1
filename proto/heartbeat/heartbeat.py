

from dataclasses import dataclass

from typing import Literal


@dataclass
class Heartbeat:
    timestamp : int
    component_type : Literal["SDK" , "agent"]
    component_id : int
    heartbeat_version : int




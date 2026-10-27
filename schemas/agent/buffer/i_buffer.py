

from dataclasses import dataclass

from schemas.agent.system_data_getter import test_01

from typing import List

from proto.metrics_and_reprots import metrics_and_reprots






@dataclass
class System_datas:
    metric_10s: test_01.Metric_10s
    metrics_500ms: List[test_01.Metric_500ms]


@dataclass
class Buffer_output:
    timestamp: float
    system_datas: System_datas
    sdk_shemas: List[metrics_and_reprots.SDK_reprot_shema]



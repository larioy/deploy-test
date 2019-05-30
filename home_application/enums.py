# -*- coding: utf-8 -*-


class RUN_TYPE:
    def __init__(self):
        pass

    NOW = 'NOW'
    TIMER = 'TIMER'
    CYCLE = 'CYCLE'


class CHECK_STATUS_TYPE:
    def __init__(self):
        pass

    WAITING = 'WAITING'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    FAIL = "FAIL"


class HEALTH_LEVLE:
    def __init__(self):
        pass

    A = "优秀"
    B = "良好"
    C = "一般"
    D = "较差"


class INTERVAL_TYPE:
    def __init__(self):
        pass

    DAY = "D"
    HOUR = "H"


ErrorText = {
    "partition": "磁盘空间不足",
    "service": "系统服务异常",
    "syserr": "发现系统错误日志",
    "apperr": "发现应用错误日志",
    "cpu_performance": "CPU性能不足",
    "memory_performance": "内存性能不足",
    "disk_performance": "磁盘性能不足"
}

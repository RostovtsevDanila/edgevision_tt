from threading import Lock


class DataDriverMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DataDriver(metaclass=DataDriverMeta):
    value: int = 0

    def add_data(self, val):
        self.value += val

    def obnulis(self):
        self.value = 0

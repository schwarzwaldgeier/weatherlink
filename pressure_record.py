class PressureRecord:
    def __init__(self, time, pressure):
        self.time = time
        self.pressure = pressure

    def __str__(self):
        return f"PressureRecord({self.time}, {self.pressure})"

    def __repr__(self):
        return self.__str__()
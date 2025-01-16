class WindRecord:
    def __init__(self, timestamp, avg_speed, max_speed, avg_direction, max_direction):
        self.timestamp = timestamp
        self.avg_speed = avg_speed
        self.max_speed = max_speed
        self.avg_direction = avg_direction
        self.max_direction = max_direction

    def __str__(self):
        return f"WindRecord({self.timestamp},{self.avg_speed}, {self.max_speed}, {self.avg_direction}, {self.max_direction})"

    def __repr__(self):
        return self.__str__()
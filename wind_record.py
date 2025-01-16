class WindRecord:
    def __init__(self, time_start, time_end, avg_speed, max_speed, avg_direction, max_direction):
        self.time_start = time_start
        self.time_end = time_end
        self.avg_speed = avg_speed
        self.max_speed = max_speed
        self.avg_direction = avg_direction
        self.max_direction = max_direction

    def __str__(self):
        return f"WindRecord({self.time_start}, {self.time_end}, {self.avg_speed}, {self.max_speed}, {self.avg_direction}, {self.max_direction})"

    def __repr__(self):
        return self.__str__()
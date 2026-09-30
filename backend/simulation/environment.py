class Environment:
    def __init__(self):
        self.road_boundaries = []
        self.obstacles = []

    def add_boundary_line(self, x1, y1, x2, y2):
        self.road_boundaries.append(((x1, y1), (x2, y2)))

    def clear(self):
        self.road_boundaries = []
        self.obstacles = []

    def get_state(self):
        return {
            "boundaries": self.road_boundaries,
            "obstacles": self.obstacles
        }

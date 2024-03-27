# Crete a class for Player
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.has_arrow = True
        self.has_gold = False
        self.direction = "east"
        self.alive = True

    # Player position
    def get_player_position(self):
        return self.x, self.y

    def set_player_position(self, x, y):
        self.x = x
        self.y = y

    # Player direction
    def get_player_direction(self):
        return self.direction

    def set_player_direction(self, direction):
        self.direction = direction

    # Player Arrow
    def set_has_arrow(self, has_arrow):
        self.has_arrow = has_arrow

    def get_has_arrow(self):
        return self.has_arrow

    # Player Gold
    def set_has_gold(self, has_gold):
        self.has_gold = has_gold

    def get_has_gold(self):
        return self.has_gold

    # Player Mortality
    def get_alive(self):
        return self.alive

    def set_alive(self, alive):
        self.alive = alive

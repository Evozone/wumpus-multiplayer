# Imports
import cell
import random
import player
import instructions

import random


def generate_seed():
    # Create a list of all possible coordinates
    coordinates = [(x, y) for x in range(8) for y in range(8)]

    # Shuffle the list
    random.shuffle(coordinates)

    # Select the first 6 coordinates as the wumpus, pits, and gold
    wumpus = coordinates[0]
    pit1 = coordinates[1]
    pit2 = coordinates[2]
    pit3 = coordinates[3]
    pit4 = coordinates[4]
    gold = coordinates[5]

    # Flatten the tuples and return as the seed
    seed = [
        coord for tuple in [wumpus, pit1, pit2, pit3, pit4, gold] for coord in tuple
    ]

    return seed


# Class for Game state
class Game:
    # Constructor
    def __init__(self, seed):
        self.seed = seed
        self.board = []
        self.sensors = {
            "breeze": False,
            "stench": False,
            "glitter": False,
            "bump": False,
            "scream": False,
        }
        self.previous_sensors = {
            "breeze": False,
            "stench": False,
            "glitter": False,
            "bump": False,
            "scream": False,
        }
        self.player = player.Player(0, 0)
        self.game_over = False
        self.game_won = False
        self.size_of_cave = 8
        self.num_pits = 4

    # Create the 8x8 game board (the cave)
    def create_board(self):
        board = []
        for i in range(8):
            row = []
            for j in range(8):
                row.append(cell.Cell(i, j))
            board.append(row)
        return board

    # Set the wumpus location
    def set_wumpus(self):
        x = self.seed[0]
        y = self.seed[1]

        # Set the wumpus in the cell
        self.board[x][y].set_wumpus(True)

        # Set the stench sensor to true for all adjacent cells
        if x > 0:
            self.board[x - 1][y].set_stench(True)
        if x < 7:
            self.board[x + 1][y].set_stench(True)
        if y > 0:
            self.board[x][y - 1].set_stench(True)
        if y < 7:
            self.board[x][y + 1].set_stench(True)

    # Set the pit locations
    def set_pits(self):
        # Four pits are placed in the cave
        for i in range(self.num_pits):
            x = self.seed[2 + (i * 2)]
            y = self.seed[3 + (i * 2)]

            # Set the pit in the cell
            self.board[x][y].set_pit()

            # Set the breeze sensor to true for all adjacent cells
            if x > 0:
                self.board[x - 1][y].set_breeze()
            if x < 7:
                self.board[x + 1][y].set_breeze()
            if y > 0:
                self.board[x][y - 1].set_breeze()
            if y < 7:
                self.board[x][y + 1].set_breeze()

    # Set the gold location
    def set_gold(self):
        x = self.seed[6]
        y = self.seed[7]

        # If the gold is placed in the starting cell or a pit, move it to a random cell
        while (x == 0 and y == 0) or self.board[x][y].get_pit():
            x = random.randint(0, 7)
            y = random.randint(0, 7)

        # Set the gold in the cell
        self.board[x][y].set_gold(True)

    # Set the initial state of the game board
    def set_initial_state(self):
        self.board = self.create_board()
        self.set_wumpus()
        self.set_pits()
        self.set_gold()

    # Print the game board like a matrix using +, -, and |
    def print_board(self):
        # Where is the player?
        player_x, player_y = self.player.get_player_position()
        player_direction = self.player.get_player_direction()

        # Print the top border
        print("+" + "---+" * 8)

        # Print the board
        for i in range(8):
            for j in range(8):
                if i == player_x and j == player_y:
                    # If player direction is north, print ^, else if player direction is east, print >, etc.
                    if player_direction == "north":
                        print("| ^ ", end="")
                    elif player_direction == "east":
                        print("| > ", end="")
                    elif player_direction == "south":
                        print("| v ", end="")
                    elif player_direction == "west":
                        print("| < ", end="")
                else:
                    print("|   ", end="")
            print("|")
            print("+" + "---+" * 8)

    # Update the sensors for gold, breeze, and stench
    def update_sensors(self):
        x, y = self.player.get_player_position()
        cell = self.board[x][y]
        self.sensors["glitter"] = cell.get_glitter()
        self.sensors["breeze"] = cell.get_breeze()
        self.sensors["stench"] = cell.get_stench()

    # Update game state using the action
    def update_game_state(self, action, step_by_step=False):
        # Determine if the action is a movement, direction change, or interaction
        if action in ["w", "s"]:
            self.move_player(action)

            x, y = self.player.get_player_position()

            # Check if the player is in a cell with a wumpus or pit after moving
            if self.board[x][y].get_wumpus():
                self.player.set_alive(False)
                print("You were eaten by the Wumpus!") if step_by_step else None
                input("Press enter to continue...") if step_by_step else None
            elif self.board[x][y].get_pit():
                self.player.set_alive(False)
                print("You fell into a pit and died!") if step_by_step else None
                input("Press enter to continue...") if step_by_step else None

        elif action in ["a", "d"]:
            self.change_direction(action)

        elif action in ["g", "q", "x"]:
            # Sensor for scream is updated inside interact
            self.interact(action, step_by_step)

        # Update the sensors for gold, breeze, and stench after the action
        self.update_sensors()

        # If the player is dead after the action, the game is over
        if not self.player.get_alive():
            self.game_over, self.game_won = True, False
            return

        # If the player is in 0, 0 with the gold, the game is over and the player wins
        if self.player.get_player_position() == (0, 0) and self.player.get_has_gold():
            self.game_over = True
            self.game_won = True

    # Move the player
    def move_player(self, action):
        # Define a dictionary that maps actions to position changes
        action_to_delta = {"w": 1, "s": -1}

        # Get the current direction and position
        direction = self.player.get_player_direction()
        x, y = self.player.get_player_position()

        # Get the change in x and y based on the direction
        delta_x, delta_y = 0, 0
        if direction == "north":
            delta_x = -action_to_delta[action]
        elif direction == "east":
            delta_y = action_to_delta[action]
        elif direction == "south":
            delta_x = action_to_delta[action]
        elif direction == "west":
            delta_y = -action_to_delta[action]

        # Calculate the new position
        new_x, new_y = x + delta_x, y + delta_y

        # Check if the new position is out of bounds
        if (
            new_x < 0
            or new_x >= self.size_of_cave
            or new_y < 0
            or new_y >= self.size_of_cave
        ):
            # If so, set the bump sensor to true and don't move the player
            self.sensors["bump"] = True

            return

        # Move the player and update the sensors
        self.player.set_player_position(new_x, new_y)

        self.sensors["bump"] = False

    # Change the direction of the player
    def change_direction(self, action):
        DIRECTIONS = ["north", "east", "south", "west"]
        # Directions are a to the left and d to the right
        # Define a dictionary that maps actions to direction changes
        action_to_delta = {"a": -1, "d": 1}

        # Get the current direction and position
        direction = self.player.get_player_direction()

        # Get the change in direction based on the action
        delta = action_to_delta[action]

        # Calculate the new direction
        new_direction = DIRECTIONS[(DIRECTIONS.index(direction) + delta) % 4]

        # Change the direction of the player
        self.player.set_player_direction(new_direction)
        # The position of the player doesn't change
        x, y = self.player.get_player_position()
        self.player.set_player_position(x, y)

    # Interact with the environment
    def interact(self, action, step_by_step=False):
        if action == "g":
            # Grab the gold if the player is on the same cell as the gold
            x, y = self.player.get_player_position()
            if self.board[x][y].get_gold():
                self.board[x][y].set_gold(False)
                self.player.set_has_gold(True)
                self.sensors["glitter"] = False
            else:
                print("There is no gold here!") if step_by_step else None
                input("Press enter to continue...") if step_by_step else None

        elif action == "q":
            # Quit the game
            self.game_over = True

        # Else if action is to shoot an arrow
        elif action == "x":
            # Check if the player has an arrow
            if self.player.get_has_arrow():
                self.player.set_has_arrow(False)
                self.shoot_arrow()
            else:
                print("You don't have an arrow!") if step_by_step else None
                input("Press enter to continue...") if step_by_step else None

    # Shoot the arrow
    def shoot_arrow(self):
        # Get the current position and direction of the player
        x, y = self.player.get_player_position()
        arrow_direction = self.player.get_player_direction()

        arrow_cells = [(x, y)]

        if arrow_direction == "north":
            for i in range(x - 1, -1, -1):
                arrow_cells.append((i, y))
        elif arrow_direction == "east":
            for i in range(y + 1, self.size_of_cave):
                arrow_cells.append((x, i))
        elif arrow_direction == "south":
            for i in range(x + 1, self.size_of_cave):
                arrow_cells.append((i, y))
        elif arrow_direction == "west":
            for i in range(y - 1, -1, -1):
                arrow_cells.append((x, i))

        # Check if the arrow hits the wumpus
        for cell in arrow_cells:
            if self.board[cell[0]][cell[1]].get_wumpus():
                self.kill_wumpus(cell[0], cell[1])
                return

    # Kill wumpus and remove stench from surrounding cells
    def kill_wumpus(self, x, y):
        # Check if the cell has a wumpus
        if self.board[x][y].get_wumpus():
            self.board[x][y].set_wumpus(False)
            self.sensors["scream"] = True

            # Remove the stench from the surrounding cells
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if (
                        i >= 0
                        and i < self.size_of_cave
                        and j >= 0
                        and j < self.size_of_cave
                    ):
                        self.board[i][j].set_stench(False)

    def print_sensors(self):
        # In human like language. Whatever is true is printed.
        if self.sensors["breeze"]:
            print("You feel a breeze. Something cold, dark and deep is nearby.")
        if self.sensors["stench"]:
            print("You smell a stench. Ew!")
        if self.sensors["glitter"]:
            print("You see a glitter. Something shiny!")
        if self.sensors["bump"]:
            print("You bump into a wall. Ouch!")
        if self.sensors["scream"]:
            print("You hear a wild, blood-curdling scream.")

    def reset_sensors(self):
        self.sensors = {
            "breeze": False,
            "stench": False,
            "glitter": False,
            "bump": False,
            "scream": False,
        }

    def print_previous_sensors(self):
        print(self.previous_sensors)

    def game_loop(self):
        instructions.display_concise_instructions()
        print("-" * 50)
        self.print_board()
        print("-" * 50)
        self.update_sensors()
        self.print_sensors()
        print("-" * 50)
        self.previous_sensors = self.sensors.copy()
        self.reset_sensors()

    def start_game(self):
        self.set_initial_state()
        self.game_loop()


if __name__ == "__main__":
    print("game.py test")
    seed = generate_seed()
    game = Game(seed)

    game.get_state()

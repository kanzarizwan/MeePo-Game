"""
Assignment 1: Meepo is You

=== CSC148 Winter 2021 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the Game class and the main game application.
"""

from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack
import actor


class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]
    pause: bool

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None
        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()
        self.player = None
        self.map_data = []
        self.keys_pressed = None
        self.pause = False

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:  # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self):
                            self._history.push(save)
                            self.win_or_lose()
                return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """
        curr = self._curr_rules()

        for rule in curr:
            if rule not in self._rules:
                self._rules.append(rule)

        reverse = []
        for rule in self._rules:
            if rule not in curr:
                reverse.append(rule)

        for rule in reverse:
            char = self.get_character(rule[0: rule.rindex(" is")])
            for obj in self.get_actors():
                if isinstance(obj, char) and isinstance(obj, actor.Character):
                    self._reverse(obj, rule[rule.rindex(" is") + 3:])
            self._rules.remove(rule)

        for rule in self._rules:
            self._handle_rule(rule)
        return

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        self.pause = False
        if not self._history.is_empty():
            prev_state = self._history.pop()
            prev_state.run()
            return

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()
        game_copy.load_map(MAP_PATH)
        game_copy.screen = self.screen
        game_copy.background = self.background
        game_copy._history = self._history

        for rule in self._rules:
            game_copy._rules.append(rule)

        for ac in self.get_actors():
            game_copy._actors.append(ac.copy())

        for ac in self._is:
            game_copy._is.append(ac.copy())

        game_copy.player = self.player.copy()
        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.pause = True
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")

    # HELPER FUNCTIONS
    def _curr_rules(self) -> List[str]:
        """
        Creates a list of all rules present on the board
        """
        curr = []
        actors = self.get_actors()
        for obj in actors:
            if isinstance(obj, actor.Is):
                up, down, left, right = self.get_actor(obj.x, obj.y - 1),\
                                        self.get_actor(obj.x, obj.y + 1), \
                                        self.get_actor(obj.x - 1, obj.y), \
                                        self.get_actor(obj.x + 1, obj.y)

                rule_1, rule_2 = obj.update(up, down, left, right)
                if rule_1 != "":
                    curr.append(rule_1)
                if rule_2 != "":
                    curr.append(rule_2)
        return curr

    def _reverse(self, obj: actor.Character, attribute: str) -> None:

        """
        Reverses the rules that are not present on the game anymore.
        """
        if attribute == "Push":
            obj.unset_push()
        elif attribute == "Stop":
            obj.unset_stop()
        elif attribute == "Victory":
            obj.unset_win()
        elif attribute == "Lose":
            obj.unset_lose()
        else:
            obj.unset_player()
            self.player = None

    def _handle_rule(self, rule: str) -> None:

        """
        Handles all the rules in self._rules
        """

        subject = rule[0: rule.rindex(" is")]
        attribute = rule[rule.rindex(" is") + 3:]
        char = self.get_character(subject)
        for obj in self.get_actors():
            if isinstance(obj, char) and isinstance(obj, actor.Character):
                if attribute == "Push":
                    if obj.is_player():
                        self.player = None
                        self._backup_player()
                    obj.set_push()
                elif attribute == "Stop":
                    if obj.is_player():
                        self.player = None
                        self._backup_player()
                    obj.set_stop()
                elif attribute == "Victory":
                    obj.set_win()
                elif attribute == "Lose":
                    obj.set_lose()
                else:  # You
                    if self.player is None and self.pause:
                        pass
                    else:
                        if self.player is not None and isinstance(self.player,
                                    actor.Character):
                            self.player.unset_player()
                        obj.set_player()
                        self.player = obj
                        if isinstance(obj, actor.Wall):
                            break
        return

    def get_actors_list(self, x: int, y: int) -> Optional[List[actor.Actor]]:
        """
        Creates a list of actors at a position on thr board.
        """
        lst = []
        for ac in self.get_actors():
            if ac.x == x and ac.y == y:
                lst.append(ac)
        if len(lst) == 0:
            return None
        return lst

    def _backup_player(self):

        lst = []
        for rule in self._rules:
            attribute = rule[rule.rindex(" is") + 3:]
            if attribute == "You":
                lst.append(rule)

        if len(lst) == 2 and self.pause is False:
            rule = lst[0]
            subject = rule[0: rule.rindex(" is")]
            char = self.get_character(subject)
            for obj in self.get_actors():
                if isinstance(obj, char):
                    obj.set_player()
                    self.player = obj
                    break
        else:
            pass



if __name__ == "__main__":
    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.run()

    # import python_ta
    # python_ta.check_all(config={'extra-imports': ['settings',
    #                                              'stack', 'actor', 'pygame']})

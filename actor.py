"""
Assignment 1: Meepo is You

=== CSC148 Winter 2021 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the Actor class and all its subclasses that represent
different types of elements in the game.
"""

import pygame
from typing import Tuple, Optional
from settings import *


class Actor:
    """
    A class that represents all the actors in the game. This class includes any
    attributes/methods that are common between the actors

    === Public Attributes ===
    x:
        x coordinate of this actor's location on the stage
    y:
        y coordinate of this actor's location on the stage
    image:
        the image of the actor

    === Private Attributes ===
    _is_stop:
        Flag to keep track of whether this object cannot be moved through
    _is_push:
        Flag to keep track of whether this object is pushable

    Representation Invariant: x,y must be greater or equal to 0
    """
    x: int
    y: int
    _is_stop: bool
    _is_push: bool
    image: pygame.Surface

    def __init__(self, x: int, y: int) -> None:

        self.x, self.y = x, y
        self._is_stop = False
        self._is_push = False
        self.image = pygame.Surface((TILESIZE, TILESIZE))

    def is_stop(self) -> bool:
        """
        Getter for _is_stop
        """
        return self._is_stop

    def is_push(self) -> bool:
        """
        Getter for _is_push
        """
        return self._is_push

    def copy(self) -> 'Actor':
        """
        Creates an identical copy of self and returns the new copy
        To be implemented in the subclasses
        """
        raise NotImplementedError

    def move(self, game_: 'Game', dx: int, dy: int) -> bool:
        """
        Function to move an Actor on the screen, to the direction
        indicated by dx and dy

        game_: the Game object
        dx: the offset in the x coordinate
        dx: the offset in the y coordinate

        Returns whether <self> actually moves.

        Note: this method is different from the "player_move" method in the
        Character class. A "player_move" is trigger by key pressed directly.
        This more general "move" can be a move caused by a push. In fact, this
        "move" method is used in the implementation of "player_move".

        Things to think about in this method:
        - The object cannot go off the screen boundaries
        - The move may push other objects to move as well.
        - The move might not happen because it's blocked by an unmovable object,
          in which case this method should return False
        - Recall how push works: you may push and move a line of multiple
          objects as long as the move is not blocked by something.
        """
        new_x, new_y = self.x + dx, self.y + dy
        # Check if the new position is in the screen frame
        if (0 <= new_x <= game_.x_tiles) and (0 <= new_y <= game_.y_tiles):
            # Check if the new position is not occupied by another object
            act = game_.get_actors_list(new_x, new_y)
            if act is None:
                self.x, self.y = new_x, new_y
                return True
            else:
                if len(act) == 1:
                    obj = act[0]
                    if (obj.is_push() is False) and (obj.is_stop()):
                        return False
                    elif (obj.is_push() is False) and (obj.is_stop() is False):
                        self.x, self.y = new_x, new_y
                        return True
                    else:  # object is pushable
                        if obj.move(game_, dx, dy):
                            self.x, self.y = new_x, new_y
                            return True
                        else:
                            return False
                else:
                    allowed = False
                    for item in act:
                        if item.is_push():
                            if item.move(game_, dx, dy):
                                allowed = True
                    if allowed:
                        self.x, self.y = new_x, new_y
                        return True
        else:
            return False


class Character(Actor):
    """
    A class that represents non-Blocks/Bushes on the screen
    i.e., Meepo, Wall, Rock, Flag

    A Character could potentially be the player that is controlled by the
    key presses

    === Additional Private Attributes ===
    _is_player:
        Whether the character is the player, i.e., "<Character> isYou"
    _is_lose:
        Whether the rules contains "<Character> isLose"
    _is_win:
        Whether the rules contains "<Character> isWin"
    """
    _is_player: bool
    _is_lose: bool
    _is_win: bool
    word: str

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes the Character
        """
        super().__init__(x, y)
        self._is_player = False
        self._is_lose = False
        self._is_win = False

    def is_win(self) -> bool:
        """
        Getter for _is_win
        """
        return self._is_win

    def is_lose(self) -> bool:
        """
        Getter for _is_lose
        """
        return self._is_lose

    def is_player(self) -> bool:
        """
        Getter for _is_player
        """
        return self._is_player

    def set_player(self) -> None:
        """
        Sets flag to make this actor the player.
        """
        self._is_player = True
        self._is_stop = False
        self._is_push = False

    def unset_player(self) -> None:
        """
        Unsets the flag to make the actor not the player.
        """
        self._is_player = False

    def set_stop(self) -> None:
        """
        Sets flag to make actor incapable of being moved through or pushed.
        """
        self._is_stop = True
        self._is_push = False
        self._is_player = False

    def unset_stop(self) -> None:
        """
        Unsets the flag that prevents actor from being moved through or pushed.
        """
        self._is_stop = False

    def set_push(self) -> None:
        """
        Sets the flag that allows the actor to be pushable
        """
        self._is_push = True
        self._is_stop = False
        self._is_player = False

    def unset_push(self) -> None:
        """
        Unsets the flag that allows the actor to be pushable
        """
        self._is_push = False

    def set_win(self) -> None:
        """
        Sets this actor to be the win Condition.
        """
        self._is_win = True
        self._is_lose = False

    def unset_win(self) -> None:
        """
        Unsets this actor from being the win Condition.
        """
        self._is_win = False

    def set_lose(self) -> None:
        """
        Sets this flag to be the lose condition.
        """
        self._is_lose = True
        self._is_win = False

    def unset_lose(self) -> None:
        """
        Unsets this flag from being the lose condition.
        """
        self._is_lose = False

    def copy_flags(self, other: "Character") -> None:
        """
        Copy the boolean flags to the <other> object
        This is a helper method that should be used by the copy methods
        implemented in the subclasses.
        """
        other._is_player = self._is_player
        other._is_push = self._is_push
        other._is_stop = self._is_stop
        other._is_lose = self._is_lose
        other._is_win = self._is_win

    def copy(self) -> 'Character':
        """
        Returns a copy of this object itself.
        Need to be implemented in the subclasses
        """
        raise NotImplementedError

    def handle_key_press(self, game_: 'Game') -> Tuple[int, int]:
        """
        Process the key press input and
        return (dx, dy), the offsets on the x and y directions.
        """
        key_pressed = game_.keys_pressed
        dx, dy = 0, 0
        if key_pressed[pygame.K_LEFT]:
            dx -= 1
        elif key_pressed[pygame.K_RIGHT]:
            dx += 1
        elif key_pressed[pygame.K_UP]:
            dy -= 1
        elif key_pressed[pygame.K_DOWN]:
            dy += 1
        return dx, dy

    def player_move(self, game_: 'Game') -> bool:
        """
        Detects input from the keyboard and moves the Player on the game stage
        based on directional key presses.

        Also, after the move, check if we have won or lost the game,
        and call the win() and lose() methods in Game accordingly
        """
        dx, dy = self.handle_key_press(game_)
        if dx == 0 and dy == 0:
            return False
        return self.move(game_, dx, dy)


class Meepo(Character):
    """
    Class representing Ms. Meepo in the game.

    Meepo is a special Character because we want to change her image as
    she moves in different directions. We also want to see the movement of
    her "arms" as she moves.

    === Additional Public Attributes ===
    walk_right:
        Image for walking right
    walk_left:
        Image for walking left
    walk_up:
        Image for walking up
    walk_down:
        Image for walking down
    """

    walk_left: list
    walk_right: list
    walk_down: list
    walk_up: list

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes the Meepo Class
        Load the images for displaying Ms. Meepo's movement.
        """
        super().__init__(x, y)
        self.word = CHARACTERS["2"]
        # Add motion images
        self.walk_right = [load_image(PLAYER_SPRITE_R1),
                           load_image(PLAYER_SPRITE_R2)]
        self.walk_left = [
            pygame.transform.flip(load_image(PLAYER_SPRITE_R1), True, False),
            pygame.transform.flip(load_image(PLAYER_SPRITE_R2), True, False)
        ]
        self.walk_up = [load_image(PLAYER_SPRITE_U1),
                        load_image(PLAYER_SPRITE_U2)]
        self.walk_down = [load_image(PLAYER_SPRITE_B1),
                          load_image(PLAYER_SPRITE_B2)]
        self.image = self.walk_down[1]

    def copy(self) -> 'Meepo':
        """
        Creates an identical copy of self and returns the new copy
        """
        new = Meepo(self.x, self.y)
        self.copy_flags(new)
        return new

    def handle_key_press(self, game_: 'Game') -> Tuple[int, int]:
        """
        Overriding the same method in the base class, adding the modification
        of the image depending on the direction of the move.
        """

        dx, dy = super().handle_key_press(game_)
        curr_image = self.image
        if dx == -1:
            if curr_image == self.walk_left[0]:
                self.image = self.walk_left[1]
            else:
                self.image = self.walk_left[0]
        elif dx == 1:
            if curr_image == self.walk_right[0]:
                self.image = self.walk_right[1]
            else:
                self.image = self.walk_right[0]
        elif dy == -1:
            if curr_image == self.walk_up[0]:
                self.image = self.walk_up[1]
            else:
                self.image = self.walk_up[0]
        elif dy == 1:
            if curr_image == self.walk_down[0]:
                self.image = self.walk_down[1]
            else:
                self.image = self.walk_down[0]
        return dx, dy


class Wall(Character):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = load_image(WALL_SPRITE)
        self.word = CHARACTERS["3"]

    def copy(self) -> 'Wall':
        """
        Creates an identical copy of self and returns the new copy
        """
        new = Wall(self.x, self.y)
        self.copy_flags(new)
        return new


class Rock(Character):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = load_image(ROCK_SPRITE)
        self.word = CHARACTERS["4"]

    def copy(self) -> 'Rock':
        """
        Creates an identical copy of self and returns the new copy
        """
        new = Rock(self.x, self.y)
        self.copy_flags(new)
        return new


class Flag(Character):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image = load_image(FLAG_SPRITE)
        self.word = CHARACTERS["5"]

    def copy(self) -> 'Flag':
        """
        Creates an identical copy of self and returns the new copy
        """
        new = Flag(self.x, self.y)
        self.copy_flags(new)
        return new


class Bush(Actor):
    """
    Class representing the edges and unmovable objects in the game.
    """
    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)
        self.image = load_image(BUSH_SPRITE)

        # Bush is always unmovable and cannot be moved through
        self._is_stop = True
        self._is_push = False

    def copy(self) -> 'Bush':
        """
        Returns a copy of the Bush object
        """
        return Bush(self.x, self.y)


class Block(Actor):
    """
    Class for words in the game such as
    "Meepo", "you", "is", "rock", "lose", "victor", "flag", "push", and "stop".

    Blocks are used for indicating rules in the game.

    ================
    Additional public attribute:
    word: the word on this block
    """
    word: str

    def __init__(self, x: int, y: int, word_: str) -> None:

        super().__init__(x, y)
        self.word = word_
        # Blocks are always pushable and cannot be moved through.
        self._is_push = True
        self._is_stop = True

    def copy(self) -> 'Block':
        """
        Creates an identical copy of self and returns the new copy.
        To be implemented in the subclasses
        """
        raise NotImplementedError


class Subject(Block):
    """
    Class representing the Subject blocks in the game, e.g.,
    "Meepo", "Wall", "Flag", "Rock" (see SUBJECTS in settings.py)
    """

    def __init__(self, x: int, y: int, word_: str) -> None:
        super().__init__(x, y, word_)
        image = WORDS_SPRITES.get(self.word.lower())
        if image is not None:
            self.image = load_image(image)

    def copy(self) -> 'Subject':
        """
        Creates an identical copy of self and returns the new copy
        """
        return Subject(self.x, self.y, self.word)


class Attribute(Block):
    """
    Class representing the Attribute blocks in the game, e.g.,
    "Push", "Stop", "Victory", "Lose", "You"
    """
    def __init__(self, x: int, y: int, word_: str) -> None:
        super().__init__(x, y, word_)
        image = WORDS_SPRITES.get(self.word.lower())
        if image is not None:
            self.image = load_image(image)

    def copy(self) -> 'Attribute':
        """
         Creates an identical copy of self and returns the new copy
         """
        return Attribute(self.x, self.y, self.word)


class Is(Block):
    """
    Class representing the Is blocks in the game.
    """

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y, " is")  # Note the space in " is"
        self.image = load_image(IS_PURPLE)

    def copy(self) -> 'Is':
        """
        Creates an identical copy of self and returns the new copy
        """
        return Is(self.x, self.y)

    def update(self, up: Optional[Actor],
               down: Optional[Actor],
               left: Optional[Actor],
               right: Optional[Actor]) -> Tuple[str, str]:
        """
        Detect horizontally and vertically if a new rule has been created in
        the format of a string "Subject isAttribute".

        up, down, left, right: the Actors that are adjacent (in the four
        directions) to this IS block

        Return a tuple of (horizontal, vertical) rules if a rule is detected
        in either direction, otherwise put an empty string at the tuple index.

        Some example return values:
        - ("Wall isPush", "Flag isWin)"
        - ("", "Rock isYou")
        - ("", "")

        Also, use IS images with different colours:
        - if no rule is detected on this IS block, use IS_PURPLE
        - if one rule is detected on this IS block, use IS_LIGHT_BLUE
        - if two rules are detected on this IS block, use IS_DARK_BLUE

        Note: We always read the rule left-to-right or up-to-down, e.g.,
        if it reads "Push is Wall" from left to right, or from bottom to top,
        it is NOT a valid rule.

        Hint: you may use the built-in method isinstance() to check the class
        type of an object.
        """

        horizontal, vertical = "", ""
        # Check if a rule is present horizontally
        if (isinstance(left, Subject)) and (isinstance(right, Attribute)):
            horizontal = SUBJECTS[left.word.upper()[0]] + self.word + \
                       ATTRIBUTES[right.word.upper()[0]]
        # Check if a rule is present vertically
        if (isinstance(up, Subject)) and (isinstance(down, Attribute)):
            vertical = SUBJECTS[up.word.upper()[0]] + self.word +\
                       ATTRIBUTES[down.word.upper()[0]]

        if (horizontal == "") and (vertical == ""):
            self.image = load_image(IS_PURPLE)
        elif (horizontal != "") and (vertical != ""):
            self.image = load_image(IS_DARK_BLUE)
        else:
            self.image = load_image(IS_LIGHT_BLUE)
        return horizontal, vertical


def load_image(img_name: str, width: int = TILESIZE,
               height: int = TILESIZE) -> pygame.image:
    """
    Return a pygame img of the PNG img_name that has been scaled according
    to the given width and size
    """
    img = pygame.image.load(img_name).convert_alpha()
    return pygame.transform.scale(img, (width, height))


if __name__ == "__main__":

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    })

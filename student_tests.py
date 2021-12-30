from game import *
from actor import *
import pytest
import pygame
import os

# USE PYGAME VARIABLES INSTEAD
keys_pressed = [0] * 323

# Setting key constants because of issue on devices
pygame.K_RIGHT = 1
pygame.K_DOWN = 2
pygame.K_LEFT = 3
pygame.K_UP = 4
pygame.K_LCTRIL = 5
pygame.K_z = 6
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
UP = pygame.K_UP
CTRL = pygame.K_LCTRL
Z = pygame.K_z


def setup_map(map: str) -> 'Game':
    """Returns a game with map1"""
    game = Game()
    game.new()
    game.load_map(os.path.abspath(os.getcwd()) + '/maps/' + map)
    game.new()
    game._update()
    game.keys_pressed = keys_pressed
    return game


def set_keys(up, down, left, right, CTRL=0, Z=0):
    keys_pressed[pygame.K_UP] = up
    keys_pressed[pygame.K_DOWN] = down
    keys_pressed[pygame.K_LEFT] = left
    keys_pressed[pygame.K_RIGHT] = right


def test1_move_player_up():
    """
    Check if player is moved up correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.y == 1


def test2_push_block():
    """
    Check if player pushes block correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
    [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][0]
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 3
    assert wall.x == 4


def test3_create_rule_wall_is_push():
    """
    Check if player creates wall is push rule correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
    [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][0]
    result = game.player.player_move(game)
    game._update()
    assert "Wall isPush" in game._rules
    assert game.player.x == 3
    assert wall.x == 4


def test_4_follow_rule_wall_is_push():
    """
    Check if player follows rules correctly
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 3


def test_5_no_push():
    """
    Check if player is not able to push because of rule not existing
    """
    game = setup_map("student_map4.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 2


def test_6_wall_lose():
    """
    Check if player is None after hitting the wall
    """
    game = setup_map("student_map5.txt")
    result = True
    result = right(4, result, game)
    result = down(3, result, game)
    set_keys(0, 0, 0, 1)

    result = result and game.player.player_move(game)
    game._update()
    assert "Wall isLose" in game.get_rules()
    result = down(3, result, game)

    game._update()
    game.win_or_lose()
    assert result is True
    assert game.player is None


def test_7_cont_rules():
    """
    Check if two rules are contradictory, the new one takes precedence
    """
    game = setup_map("student_map5.txt")
    result = True
    result = right(2, result, game)
    result = down(12, result, game)
    result = left(1, result, game)
    result = down(3, result, game)
    result = right(9, result, game)
    result = up(2, result, game)
    result = left(1, result, game)
    result = down(1, result, game)

    result = up(1, result, game)
    result = left(3, result, game)
    result = down(1, result, game)
    result = right(2, result, game)
    result = left(7, result, game)
    result = up(1, result, game)
    result = right(7, result, game)
    game._update()

    assert result is True
    assert game.player is None


def test_8_coexist():
    """
    Check if two rules of the same attribute, lose, can coexist
    """
    game = setup_map("student_map5.txt")
    result = True

    result = right(4, result, game)
    result = down(3, result, game)
    result = right(1, result, game)
    game._update()

    result = left(1, result, game)
    result = down(1, result, game)
    result = right(2, result, game)
    result = down(6, result, game)
    result = right(1, result, game)
    result = up(4, result, game)
    result = right(2, result, game)
    result = up(3, result, game)
    result = left(2, result, game)
    result = right(1, result, game)
    result = down(3, result, game)
    result = left(1, result, game)
    result = up(3, result, game)
    result = down(1, result, game)
    result = left(4, result, game)
    result = up(1, result, game)
    result = right(1, result, game)
    game._update()

    wall = \
        [i for i in game._actors if isinstance(i, Wall)][0]
    flag = \
        [i for i in game._actors if isinstance(i, Flag)][0]

    assert result is True
    assert wall.is_lose() is True
    assert flag.is_lose() is True


def test_9_undo():
    """
    Check if the undo feature works
    """
    game = setup_map("student_map5.txt")
    result = True

    result = right(1, result, game)
    game._history.push(game._copy())
    game._update()

    result = down(1, result, game)
    game._history.push(game._copy())
    game._update()

    game._history.pop()
    prev = game._history.pop()
    new_x, new_y = prev.player.x, prev.player.y
    assert 6 == new_x
    assert 2 == new_y
    assert result is True


def test_10_wall_player():
    """
    Check when wall is you, only one wall character is set to player
    """
    game = setup_map("student_map5.txt")
    result = True

    result = right(5, result, game)
    result = down(3, result, game)
    result = right(1, result, game)

    result = down(1, result, game)
    result = left(6, result, game)

    result = up(1, result, game)
    result = left(1, result, game)
    result = down(7, result, game)
    result = right(2, result, game)
    result = down(4, result, game)
    result = right(4, result, game)
    result = up(1, result, game)
    result = left(5, result, game)
    game._update()
    lst = []
    for act in game.get_actors():
        if game.player == act:
            lst.append(act)

    assert len(lst) == 1
    assert result is True


def test_11_two_players():
    """
    Check if two rules have the attribute 'isYou', the second one
    becomes the player
    """
    game = setup_map("student_map5.txt")
    result = True

    result = right(2, result, game)
    result = down(12, result, game)
    result = left(1, result, game)

    result = down(2, result, game)
    result = right(4, result, game)

    result = up(1, result, game)
    result = left(4, result, game)
    result = up(5, result, game)
    result = left(2, result, game)
    result = down(3, result, game)
    result = up(2, result, game)
    result = left(2, result, game)

    result = down(1, result, game)
    result = right(1, result, game)

    result = up(1, result, game)
    result = right(1, result, game)
    result = down(1, result, game)
    result = right(2, result, game)

    result = down(3, result, game)
    result = left(1, result, game)
    game._update()

    assert result is True
    assert isinstance(game.player, actor.Rock)


def test_12_second_player_blocked():
    game = setup_map("student_map5.txt")
    result = True

    result = right(2, result, game)
    result = down(12, result, game)
    result = left(1, result, game)

    result = down(2, result, game)
    result = right(4, result, game)

    result = up(1, result, game)
    result = left(4, result, game)
    result = up(5, result, game)
    result = left(2, result, game)
    result = down(3, result, game)
    result = up(2, result, game)
    result = left(2, result, game)

    result = down(1, result, game)
    result = right(1, result, game)

    result = up(1, result, game)
    result = right(1, result, game)
    result = down(1, result, game)
    result = right(2, result, game)

    result = down(3, result, game)
    result = left(1, result, game)
    game._update()

    result = right(1, result, game)
    result = down(8, result, game)
    result = right(7, result, game)
    result = up(1, result, game)
    result = left(7, result, game)
    result = up(1, result, game)
    result = left(1, result, game)
    result = down(2, result, game)
    game._update()

    assert result is True
    assert "Rock isPush" in game.get_rules()
    assert "Rock isYou" in game.get_rules()
    assert isinstance(game.player, actor.Meepo)


def test_two_player_lose():
    """
    Check the player object when there are two You rules and the
    player hits lose actor
    """

    game = setup_map("student_map5.txt")
    result = True
    result = right(4, result, game)
    result = down(3, result, game)
    result = right(1, result, game)
    game._update()

    result = left(5, result, game)
    result = down(11, result, game)
    result = right(5, result, game)

    result = up(1, result, game)
    result = left(5, result, game)

    result = up(5, result, game)
    result = left(1, result, game)
    result = down(3, result, game)
    result = left(2, result, game)
    result = up(1, result, game)
    result = right(1, result, game)

    result = up(1, result, game)
    result = right(1, result, game)
    result = down(1, result, game)
    game._update()

    result = right(3, result, game)
    result = down(3, result, game)

    game._history.push(game._copy())
    result = down(1, result, game)
    game._update()

    game.win_or_lose()
    assert result is True
    assert game.player is None

    prev = game._history.pop()
    assert isinstance(prev.player, actor.Rock)


# Helper functions for moving
def up(size: int, result: bool, game: Game) -> bool:
    for i in range(size):
        set_keys(1, 0, 0, 0)
        result = result and game.player.player_move(game)
    return result


def down(size: int, result: bool, game: Game) -> bool:
    for i in range(size):
        set_keys(0, 1, 0, 0)
        result = result and game.player.player_move(game)
    return result


def left(size: int, result: bool, game: Game) -> bool:
    for i in range(size):
        set_keys(0, 0, 1, 0)
        result = result and game.player.player_move(game)
    return result


def right(size: int, result: bool, game: Game) -> bool:
    for i in range(size):
        set_keys(0, 0, 0, 1)
        result = result and game.player.player_move(game)
    return result


if __name__ == "__main__":

    import pytest
    pytest.main(['student_tests.py'])


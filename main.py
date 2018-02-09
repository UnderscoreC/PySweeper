""" PySweeper - A small Python/PyGame remake of the classic

Written by Cyprien N, 2018
Feel free to do what you like with it.

USAGE:
- customize const.py to your liking (although default
configuration is typically fine).
- install pygame if you haven't already (`pip install pygame`)
- run main.py
"""

# pylint: disable=W0614, no-member, invalid-name, undefined-variable

import pygame
from pygame.locals import *

from obj import Terrain
from const import (
    PLOT_PADDING, PLOT_SIZE,
    TERRAIN_MARGIN, ICON
)


def get_size():
    """ Get the user disired length of the terrain side
    and return.
    """

    print("Welcome to PySweeper!")
    print("Please pick a terrain size, between 9 and 16")

    is_answer_gotten = False

    while not is_answer_gotten:
        try:
            size = int(input(
                "How long do you want your terrain side to be? "
            ))
            if size < 9:
                print("Error : input should be at least 9")
            elif size > 16:
                print("Error : Max size is 16")
            else:
                is_answer_gotten = True
        except ValueError:
            print("Error : input should be a number!")
    return size


TERRAIN_SIDE = get_size()

# Generate display size : PLOT_SIZE per plot
# PLOT_PADDING between them
# TERRAIN_MARGIN on each side

SCREEN_SIZE = (
    (PLOT_SIZE * TERRAIN_SIDE)
    + PLOT_PADDING * (TERRAIN_SIDE - 2)
    + TERRAIN_MARGIN * 2
)

terrain = Terrain(TERRAIN_SIDE)
print(terrain.get_stats())


pygame.init()

pygame.display.set_icon(ICON)
DISPLAY = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("PySweeper")

is_left_click = False
is_right_click = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type == MOUSEBUTTONDOWN:
            # Use elif because we only want one button to be
            # registered at a time
            if event.button == 1:
                is_left_click = True
            elif event.button == 3:
                is_right_click = True

        if event.type == MOUSEBUTTONUP:
            # User has lifted mouse buttons
            # Allow mouse press events back into the queue
            pygame.event.set_allowed(MOUSEBUTTONDOWN)
            if event.button == 1:
                is_left_click = False
            if event.button == 3:
                is_right_click = False


    terrain.update_plots(
        is_left_click,
        is_right_click,
        pygame.mouse.get_pos()
    )

    # Place this after plot updating.
    # This forces the user to unpress the
    # mouse before being able to press again
    # It works by blocking mouse presses
    # from entering the event queue
    # until mouseup
    if is_right_click or is_left_click:
        pygame.event.set_blocked(MOUSEBUTTONDOWN)
        is_right_click = False
        is_left_click = False


    # Render queue
    # Highest last

    DISPLAY.fill((10, 10, 10))
    terrain.render_plots(DISPLAY)
    pygame.display.update()

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

from obj import Terrain_Manager, Stat_Manager
from const import (
    PLOT_PADDING, PLOT_SIZE,
    TERRAIN_MARGIN, ICON,
    DISPLAY_HEIGHT
)


def get_size(min_size, max_size):
    """ Get the user disired length of the terrain side
    and return.
    """

    print("Welcome to PySweeper!")
    print(
        "Please pick a terrain size, between {} and {}".format(
            min_size, max_size
        )
    )

    is_answer_gotten = False

    while not is_answer_gotten:
        try:
            size = int(input(
                "How long do you want your terrain side to be? "
            ))
            if size < min_size:
                print("Error: input should be at least", min_size)
            elif size > max_size:
                print("Error: Max size is", max_size)
            else:
                is_answer_gotten = True
        except ValueError:
            print("Error: input should be a number!")
    return size


TERRAIN_SIDE = get_size(9, 64)

# Generate display size : PLOT_SIZE per plot
# PLOT_PADDING between them
# TERRAIN_MARGIN on each side
SCREEN_SIZE = (
    (PLOT_SIZE * TERRAIN_SIDE)
    + PLOT_PADDING * (TERRAIN_SIDE - 2)
    + TERRAIN_MARGIN * 2
)


terrain = Terrain_Manager(TERRAIN_SIDE)
manager = Stat_Manager(SCREEN_SIZE, terrain)

print(
    "Terrain size: {0}x{0}; "
    "Number of plots: {1}; "
    "Number of mines: {2};".format(
        *terrain.get_stats()
    )
)

# Check and warn user if SCREEN_SIZE
# is taller than display
if SCREEN_SIZE > DISPLAY_HEIGHT:
    print(
        "Warning: game terrain taller than "
        "screen height. The entire board will "
        "not fit. Modify values in const.py "
        "to resize."
    )


pygame.init()

pygame.display.set_icon(ICON)
DISPLAY = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("PySweeper")

is_left_click = False
is_right_click = False

# Just to avoid those ugly 'not initialized' messages
quit = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit = True

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

    if quit:
        break

    terrain.update_plots(
        is_left_click,
        is_right_click,
        pygame.mouse.get_pos()
    )

    manager.update_options(
        is_left_click,
        pygame.mouse.get_pos()
    )


    # Place this after plot updating.
    # This forces the user to unpress the
    # mouse before being able to press again
    # It works by blocking mouse presses
    # from entering the event queue
    if is_right_click or is_left_click:
        pygame.event.set_blocked(MOUSEBUTTONDOWN)
        is_right_click = False
        is_left_click = False


    manager.update_time()

    # Render queue
    # Highest last
    DISPLAY.fill((10, 10, 10))
    terrain.render_plots(DISPLAY)
    manager.render_statbar(DISPLAY)
    manager.render_options(DISPLAY)

    pygame.display.update()

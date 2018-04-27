""" PySweeper - A small Python/PyGame remake of the classic

Written by Cyprien N, 2018
Feel free to do what you like with it.

USAGE:
 - customize const.py to your liking (although default
   configuration is typically fine).
 - install pygame if you haven't already (`pip install pygame`)
 - run main.py
"""

# pylint: disable=unused-wildcard-import, no-member, no-name-in-module

import pygame
from pygame.constants import MOUSEBUTTONUP, MOUSEBUTTONDOWN, QUIT

from obj import Terrain_Manager, Stat_Manager
from const import ICON, TERRAIN_SIDE, SCREEN_SIZE

terrain = Terrain_Manager(TERRAIN_SIDE)
manager = Stat_Manager(SCREEN_SIZE, terrain)

print(
    "Terrain size: {0}x{0}; "
    "Number of plots: {1}; "
    "Number of mines: {2};".format(
        *terrain.get_stats()
    )
)


def main():
    pygame.init()

    pygame.display.set_icon(ICON)
    display = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("PySweeper")

    is_left_click = False
    is_right_click = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

            if event.type == MOUSEBUTTONDOWN:
                # Use elif because we only want one button to be
                # registered at a time
                if event.button == 1:
                    is_left_click = True
                elif event.button == 3:
                    is_right_click = True

                # Only need to update on mouse-click
                terrain.update_plots(
                    is_left_click,
                    is_right_click,
                    pygame.mouse.get_pos()
                )


        manager.update_options(
            is_left_click,
            pygame.mouse.get_pos()
        )

        manager.update_time()


        # Switch them so that it doesn't
        # keep registering clicks
        is_right_click = False
        is_left_click = False


        # Render queue
        # Highest last
        display.fill((10, 10, 10))
        terrain.render_plots(display)
        manager.render_statbar(display)
        manager.render_options(display)

        pygame.display.update()


if __name__ == '__main__':
    main()

print('Bye!')

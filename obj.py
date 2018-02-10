""" Objects for PySweeper. These are:
 - The Terrain (container for all the plots)
 - A Plot object that represents each individual plot
"""

# pylint: disable=W0614, no-member

from random import randrange, shuffle

import pygame
from pygame.locals import *

from const import (
    TERRAIN_MARGIN, PLOT_PADDING,
    PLOT_SIZE, PLOT_TILES
)


class Terrain():
    """ God oject class that controls generation, allocation
    and management of the terrain and its plots.
    """

    def __init__(self, terrain_side):

        # Terrain side is the number of plots
        # along one side of the game terrain
        self.terrain_side = terrain_side
        self.plot_quantity = terrain_side ** 2
        self.is_first_click = True

        self.__generate_mine_map()
        self.__generate_plots()


    def __generate_mine_map(self):
        """ Generate the map of the terrain
        and fill it randomly with mines.
        """

        self.mine_quantity = (
            10 if self.terrain_side == 9 or self.terrain_side == 10
            else randrange(
                # Int conversion rounds down
                int(self.plot_quantity / 7),
                int(self.plot_quantity / 5)
            )
        )

        # List filled with zero. These represent
        # empty plots. Mines (where the value
        # is 1) are added later
        self.mine_map = [0] * self.plot_quantity

        # Add all the mines to the mine map
        for i in range(self.mine_quantity):
            self.mine_map[i] = 1

        for i in range(10):
            shuffle(self.mine_map)


    def __generate_plots(self):
        """ Generate a container object for
        each plot. These are instances of Plot.
        """

        self.plots = []

        # Initial offsets
        # x and y are pixel coordinates
        x = y = TERRAIN_MARGIN

        # These are plot quantity offsets.
        # That is, the number of plots that have
        # be generated on this row
        x_offset = y_offset = 0

        current_row_plotcount = 0

        # Row level, starting from the top
        level = 1

        for i in range(self.plot_quantity):

            plot = Plot(
                self.mine_map[i],
                x, y,
                x_offset, y_offset
            )
            self.plots.append(plot)

            # Offset between each plot
            x += PLOT_PADDING + PLOT_SIZE
            x_offset += 1
            current_row_plotcount += 1

            # As soon as the terrain side quantity has been
            # generated once, descend one level, and repeat
            if current_row_plotcount == self.terrain_side:

                # Adjust and reset offsets
                x = TERRAIN_MARGIN
                x_offset = 0
                y_offset += 1

                y = TERRAIN_MARGIN + level * (PLOT_SIZE +
                    PLOT_PADDING)

                current_row_plotcount = 0
                level += 1


    def print_mine_map(self):
        """Print minemap, formatted to match terrain. """

        self.mine_map = []

        # Update minemap
        for plot in self.plots:
            if plot.type == 1:
                self.mine_map.append(1)
            else:
                self.mine_map.append(0)

        for i in range(self.terrain_side):
            print(
                self.mine_map[
                    i * self.terrain_side
                    : i * self.terrain_side + self.terrain_side
                ])


    def get_stats(self, minemap=False):
        """Return terrain stats for current game. """

        stats = (
            "Terrain size: {0}x{0}; ".format(self.terrain_side),
            "Number of plots: {}; ".format(self.plot_quantity),
            "Number of mines: {};".format(self.mine_quantity)
        )

        if minemap:
            self.print_mine_map()

        return stats[0] + stats[1] + stats[2]


    def render_plots(self, display):
        """Blit all plots to display. """

        for plot in self.plots:
            display.blit(plot.surface, (plot.rect.x, plot.rect.y))


    def update_plots(self, lmouse, rmouse, mouse_pos):
        """Update plots according to user interaction. """

        for plot in self.plots:
            if not plot.revealed:
                if lmouse:
                    if plot.state == 0:
                        if plot.rect.collidepoint(mouse_pos):

                            # Clicked on mined plot
                            if plot.type == 1:
                                # Player can't die on first click
                                if not self.is_first_click:
                                    plot.reveal(PLOT_TILES[14])
                                    self.reveal_all()
                                    # Return so it doesn't override
                                    # repaint over
                                    return

                                else:
                                    self.relocate_mine(plot)


                            self.is_first_click = False


                            if self.get_adjacent_mines(plot) == 0:
                                # There aren't any, check around
                                self.reveal_adjacent_plots(plot)

                            # Reveal plot according to amount of
                            # neighboring mines
                            plot.reveal(PLOT_TILES[
                                self.get_adjacent_mines(plot)
                            ])

                elif rmouse:
                    if plot.rect.collidepoint(mouse_pos):
                        plot.toggle_state()

                    # Game can only be won from a right-click
                    self.check_victory()


    def relocate_mine(self, plot):
        """ Move a mine from a plot to another one.
        Only used once per game, if the player's first
        click is on a mine.
        """

        relocated = False

        while not relocated:
            new_target = self.get_plot(
                randrange(0, self.terrain_side),
                randrange(0, self.terrain_side)
            )

            if new_target.type == 0:
                plot.type = 0
                new_target.type = 1
                relocated = True

        print("Mined plot relocated to {};{}".format(
            new_target.x_offset, new_target.y_offset
        ))
        # self.print_mine_map()


    def get_adjacent_plots(self, plot):
        """Return a list with all adjacent plots. """

        x = plot.x_offset
        y = plot.y_offset

        # Holds temporarily all the offsets to
        # get adjacent plots.
        # [x_offset_shift, y_offset_shift]
        adjacent_offsets = {
            1: [-1, -1], 2: [0, -1], 3: [1, -1],
            4: [-1, 0],              5: [1, 0],
            6: [-1, 1],  7: [0, 1],  8: [1, 1]
        }

        adjacent_plots = []

        # Shift all offsets to be relative to the clicked plot
        for pair in adjacent_offsets:
            adjacent_offsets[pair][0] += x
            adjacent_offsets[pair][1] += y

        # Get all adjacent plots according to x and y offsets
        # gotten from adjacent_offset. The last bit, `if plot`,
        # removes None elements, as they equate to False,
        # that get returned by get_plot when it finds no matches.
        # This happens because plots offsets can be out of bounds
        adjacent_plots = [
            plot for plot in [
                self.get_plot(
                    adjacent_offsets[pair][0],
                    adjacent_offsets[pair][1]
                ) for pair in adjacent_offsets
            ] if plot
        ]

        return adjacent_plots


    def get_adjacent_mines(self, plot):
        """ Return the quantity of mines adjacent
        to plot.
        """

        quantity = len([
            plot for plot in
            self.get_adjacent_plots(plot)
            if plot.type == 1
        ])

        return quantity


    def get_plot(self, x_offset, y_offset):
        """ Returns a plot that matches the given x_offset
        and y_offset, returns None if none were found.
        """

        for plot in self.plots:
            if (
                plot.x_offset == x_offset
                and plot.y_offset == y_offset
            ):
                return plot


    def reveal_adjacent_plots(self, plot):
        """ Reveal all adjacent plots, and those adjacent
        to them, until all plots are adjacent to mines.
        """

        adjacent_to = self.get_adjacent_plots
        adjacent_mines_to = self.get_adjacent_mines
        tile = PLOT_TILES

        plot_queue = adjacent_to(plot)
        next_queue = []

        # Empty iterables are False (PEP8)
        while plot_queue:

            for plot in plot_queue:
                if not plot.revealed:

                    if adjacent_mines_to(plot) == 0:
                        plot.reveal(tile[0])

                        for adj_plot in adjacent_to(plot):
                            if adj_plot not in next_queue:
                                next_queue.append(adj_plot)

                    else:
                        plot.reveal(tile[adjacent_mines_to(plot)])

            plot_queue = [
                plot for plot in next_queue if
                plot not in plot_queue
            ]
            next_queue = []


    def check_victory(self):
        """ Check if the player has won, by verifying that
        exclusively all plots with mines have been marked.
        """

        mines = self.mine_quantity
        marked_mines = []
        correct = 0

        marked_mines = [
            plot for plot in self.plots
            if plot.state == 1
            and plot not in marked_mines
        ]

        for plot in marked_mines:
            if plot.type == 1:
                correct += 1
            else:
                correct -= 1

        if correct == mines:
            print('WON')
            self.reveal_all()


    def reveal_all(self):
        """Unveil all the plots and their contents. """

        for plot in self.plots:
            if not plot.revealed:
                # If the plot had a mine
                if plot.type == 1:
                    # But was not marked
                    if plot.state == 0:
                        plot.reveal(PLOT_TILES[11])
                    # But was marked
                    elif plot.state == 1:
                        plot.reveal(PLOT_TILES[13])
                # If the plot was safe but was marked
                elif plot.type == 0 and plot.state == 1:
                    plot.reveal(PLOT_TILES[12])
                else:
                    plot.reveal(PLOT_TILES[
                        self.get_adjacent_mines(plot)
                    ])


class Plot():
    """ Class that represents each individual plot.
    Type can be 0 or 1: empty or mined.
    x and y are the plot's rect's coordinates.
    x_offset is the plot horizontal offset, starting
    from the left (0) and ending with SIDE - 1.
    y_offset is the same as x_offset, but vertically.
    """

    def __init__(self, type, x, y, x_offset, y_offset):
        self.state = 0
        self.type = type
        self.surface = pygame.surface.Surface((PLOT_SIZE, PLOT_SIZE))
        self.rect = self.surface.get_rect(topleft=(x, y))
        self.surface.fill((100, 100, 100))
        self.x_offset, self.y_offset = x_offset, y_offset
        self.revealed = False


    def reveal(self, tile):
        """ Reveal the contents of the plot,
        update plot tile to display `tile`.
        """

        self.revealed = True
        # The destination coordinates are relative to
        # the plot's surface.
        self.surface.blit(tile, (0, 0))


    def toggle_state(self):
        """Toggle between plot tile states. """

        self.state += 1
        self.state %= 3

        self._update_tile()


    def _update_tile(self):
        """Update tile according to state. """

        # Unmarked
        if self.state == 0:
            self.surface.fill((100, 100, 100))
        # Flagged
        elif self.state == 1:
            self.surface.blit(PLOT_TILES[9], (0, 0))
        # Neutral
        else:
            self.surface.blit(PLOT_TILES[10], (0, 0))
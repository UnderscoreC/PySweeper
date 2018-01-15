import pygame
from pygame.locals import *
from random import randrange, shuffle


from os import path

from const import PLOT_PADDING, PLOT_SIZE, TERRAIN_MARGIN


ROOT_PATH = path.dirname(__file__)
RESOURCE_PATH = path.join(ROOT_PATH, 'res')
IMAGE_PATH = path.join(RESOURCE_PATH, 'img')

PLOT_TILES = {}

for number in range(15):
    PLOT_TILES[number] = pygame.image.load(
        path.join(IMAGE_PATH, '{}.png'.format(number))
    )

class Terrain():
    """God oject class that controls generation,
    allocation and management of the terrain its plots."""

    def __init__(self, terrain_side):

        # Terrain side is the number of plots
        # along one side of the game terrain
        self.terrain_side = terrain_side
        self.plot_quantity = terrain_side ** 2

        self.__generate_mine_map()
        self.__generate_plots()


    def get_stats(self):
        """Return terrain stats for current game"""

        stats = (
            "Side : {};".format(self.terrain_side),
            "Number of plots : {};".format(self.plot_quantity),
            "Number of mines : {};".format(self.mine_quantity)
        )
        return str(stats)


    def __generate_mine_map(self):
        """Generate the map of the terrain
        and fill it randomly with mines"""

        if self.terrain_side == 9 or self.terrain_side == 10:
            self.mine_quantity = 10
        else:
            # Int type conversion rounds down
            self.mine_quantity = randrange(
                5, int(self.plot_quantity / 5)
            )

        # HACK for a list filled with 0
        self.mine_map = [x - x for x in range(self.plot_quantity)]

        # Add all the mines to the mine map
        for i in range(self.mine_quantity):
            self.mine_map[i] = 1

        # Randomly allocate all the mines
        for i in range(10):
            shuffle(self.mine_map)


    def __generate_plots(self):
        """Generate the object for each plot.
        These are instances of Plot"""

        self.plots = []

        # Initial offset
        x = y = TERRAIN_MARGIN
        x_offset = y_offset = 0

        current_row_plotcount = 0
        level = 1

        for i in range(self.plot_quantity):

            plot = Plot(
                0, self.mine_map[i],
                x, y,
                x_offset, y_offset
            )
            self.plots.append(plot)

            current_row_plotcount += 1

            # Offset between each plot
            x += PLOT_PADDING + PLOT_SIZE
            x_offset += 1

            # Once 1 times the terrain side quantity
            # has been generated, descend one level
            if current_row_plotcount == self.terrain_side:

                # Reset x offsets
                x = TERRAIN_MARGIN
                x_offset = 0

                y_offset += 1

                y = TERRAIN_MARGIN + level * (PLOT_SIZE +
                    PLOT_PADDING)
                current_row_plotcount = 0
                level += 1


    def render_plots(self, display):
        """Blit all plots to display."""

        for plot in self.plots:
            display.blit(plot.surface, (plot.rect.x, plot.rect.y))


    def update_plots(self, lmouse, rmouse, mouse_pos):
        """Manage plots according to user interaction."""

        for plot in self.plots:
            if not plot.revealed:
                if lmouse:
                    if plot.state == 0:
                        if plot.rect.collidepoint(mouse_pos):
                            # Clicked on mined plot, game over
                            if plot.type == 1:
                                plot.reveal(PLOT_TILES[14])
                                self.reveal_all()
                            # There are no adjacent mines,
                            # so check around.
                            elif self.get_adjacent_mines(plot) == 0:
                                plot.reveal(PLOT_TILES[0])
                                self.reveal_adjacent_empty_plots(plot)
                            # There are adjacent mines, show how many.
                            else:
                                plot.reveal(
                                    PLOT_TILES[
                                        self.get_adjacent_mines(plot)
                                    ])

                elif rmouse:
                    if plot.rect.collidepoint(mouse_pos):
                        plot.toggle_state()

                    # Game can only be won from a right-click
                    self.check_victory()


    def get_adjacent_plots(self, plot):
        """Return a list with all adjacent plots."""

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
        # gotten from adjacent_offset.
        # The last bit, `if plot`, removes None elements, as they
        # equate to False, that get returned by get_plot when
        # it finds no matches.
        # This happens because plots offsets can be out of bounds
        adjacent_plots = [
            plot for plot in [
                self.get_plot(
                    adjacent_offsets[pair][0],
                    adjacent_offsets[pair][1]
                ) for pair in adjacent_offsets
            ] if plot
        ]

        return(adjacent_plots)


    def get_adjacent_mines(self, plot):
        """Return the quantity of mines adjacent
        to plot."""

        quantity = len([
            plot for plot in
            self.get_adjacent_plots(plot)
            if plot.type == 1
        ])

        return quantity


    def get_plot(self, x_offset, y_offset):
        """Returns a plot that matches the given x_offset
        and y_offset, returns None if none were found."""

        for plot in self.plots:
            if(
                plot.x_offset == x_offset
                and plot.y_offset == y_offset
            ):
                return plot


    def reveal_adjacent_empty_plots(self, plot):
        adjacent_to = self.get_adjacent_plots
        adjacent_mines_to = self.get_adjacent_mines

        exhausted = False

        tile = PLOT_TILES

        adj_current = adjacent_to(plot)
        adj_next = []

        def sort(target):
            adj = adjacent_mines_to(target)
            for x in range(0, 9):
                if adj == x:
                    plot.reveal(tile[x])

        def remove_duplicates(iterable):
            for item in iterable:
                if iterable.count(item) > 1:
                    # There is more than one instance of item,
                    # remove all of them except one.
                    for i in range(iterable.count(item) - 1):
                        iterable.remove(item)

        while not exhausted:

            for plot in adj_current:
                if not plot.revealed:
                    # There are no adjacent mines
                    if adjacent_mines_to(plot) == 0:
                        plot.reveal(tile[0])

                        for plot in adjacent_to(plot):
                            if plot.type == 0:
                                adj_next.append(plot)

                    # There are adj mines
                    else:
                        sort(plot)

            remove_duplicates(adj_next)
            adj_current = []


            # No new mines have been added to
            # the queue, so all possible plots
            # have been exhausted. We're done.
            if len(adj_next) <= 0:
                exhausted = True

            for plot in adj_next:
                # There are no adj mines
                if adjacent_mines_to(plot) == 0:
                    plot.reveal(tile[0])

                    for plot in adjacent_to(plot):
                        adj_current.append(plot)

                # There are adj mines
                else:
                    sort(plot)

            adj_next = []
            remove_duplicates(adj_current)


    def check_victory(self):
        """Check if the player has won, by verifying
        that exclusivelyall plots with mines
        have been marked."""
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

    def reveal_all(self):
        """Unveil all the plots and their contents."""
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
    """Class that represents each individual plot.
    State can be 0, 1 ot 2, which respectively
    represent: unmarked, flagged, or unknown.
    Type can be 0 or 1: empty or mined.
    x and y are the plot's rect's coordinates.
    x_offset is the plot horizontal offset, starting
    from the left (0) and ending with SIDE - 1.
    y_offset is the same as x_offset, but vertically.
    """

    def __init__(self, state, type, x, y, x_offset, y_offset):
        self.state = state
        self.type = type
        self.surface = pygame.surface.Surface((PLOT_SIZE, PLOT_SIZE))
        self.rect = self.surface.get_rect(topleft=(x, y))
        self.surface.fill((100, 100, 100))
        self.x_offset, self.y_offset = x_offset, y_offset

        # The plot is revealed when left-clicked
        self.revealed = False


    def reveal(self, tile):
        """Reveal the contents of the plot,
        update tile according to surrounding mine quantity"""

        self.revealed = True

        # The dest coordinates are relative to the plot's
        # surface.
        self.surface.blit(tile, (0, 0))


    def toggle_state(self):
        """Toggle between plot tile display states."""

        if self.state < 2:
            self.state += 1
        else:
            self.state = 0

        self.update_tile()


    def update_tile(self):
        # Unmarked
        if self.state == 0:
            self.surface.fill((100, 100, 100))
        # Flagged
        elif self.state == 1:
            self.surface.blit(PLOT_TILES[9], (0, 0))
        # Unknown
        else:
            self.surface.blit(PLOT_TILES[10], (0, 0))

""" Objects for PySweeper. These are:
 - The Terrain (container for all the plots)
 - A Plot object that represents each individual plot
"""

# pylint: disable=W0614, no-member

from random import randrange, shuffle

from pygame import font, surface, time

from const import (
    TERRAIN_MARGIN, PLOT_PADDING,
    PLOT_SIZE, PLOT_TILES,
    RESOURCE_PATH, DISPLAY_HEIGHT
)

# Font preloading
font.init()
SF = {}

for size in (32, 64, int(1 / 12 * DISPLAY_HEIGHT)):
    exec(
        "SF_{0} = font.Font(RESOURCE_PATH + '\\sfm.otf', {0})".format(
            size
        )
    )
    exec("SF[{0}] = SF_{0}".format(size))


class Terrain_Manager():
    """ God oject class that controls generation, allocation
    and management of the terrain and its plots.
    """

    def __init__(self, terrain_side):
        # Terrain side is the number of plots
        # along one side of the game terrain
        self.terrain_side = terrain_side
        self.plot_quantity = terrain_side ** 2


        self.is_first_click = True
        self.playing = True
        self.marked_mines = 0
        self.plots = []

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


    def _print_mine_map(self):
        """ Print minemap, formatted to match terrain. """

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
        """ Return various game stats for current game.
        If minemap, print a map of all the mines
        """

        if minemap:
            self._print_mine_map()

        return [
            self.terrain_side, self.plot_quantity,
            self.mine_quantity, self.marked_mines
        ]


    def render_plots(self, display):
        """ Blit all plots to display. """

        for plot in self.plots:
            display.blit(plot.surface, (plot.rect.x, plot.rect.y))


    def update_plots(self, lmouse, rmouse, mouse_pos):
        """ Update plots according to user interaction. """

        if not self.playing:
            return

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
                                    print('You died!')
                                    self.reveal_all()
                                    # Return so it doesn't
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
                        state = plot.toggle_state()
                        if state == 1:
                            self.marked_mines += 1
                        elif state == 2:
                            self.marked_mines -= 1

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
        """ Return a list with all adjacent plots. """

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
        """ Returns the plot that matches the given x_offset
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

        # Get a list with the types of all marked plots
        # If the player has marked them all properly,
        # all(marked) should return True
        marked = [
            plot.type for plot in self.plots
            if plot.state == 1
        ]

        if self.marked_mines == mines:
            if all(marked):
                print('Victory!')
                self.reveal_all()


    def reveal_all(self):
        """ Unveil all the plots. Sets self.playing to False. """

        self.playing = False

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


    def restart(self):
        """ Restart new game. """
        self.is_first_click = True
        self.playing = True
        self.marked_mines = 0
        self.plots = []

        self.__generate_mine_map()
        self.__generate_plots()



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
        self.surface = surface.Surface((PLOT_SIZE, PLOT_SIZE))
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
        """ Toggle between plot tile states.
        Returns 0 if unmarked, 1 if marked,
        or 2 if unknown.
        """

        self.state += 1
        self.state %= 3
        self._update_tile()

        return self.state


    def _update_tile(self):
        """ Update tile according to state. """

        # Unmarked
        if self.state == 0:
            self.surface.fill((100, 100, 100))
        # Flagged
        elif self.state == 1:
            self.surface.blit(PLOT_TILES[9], (0, 0))
        # Unknown
        else:
            self.surface.blit(PLOT_TILES[10], (0, 0))


class Stat_Manager():
    """ Object that controls all the game's
    text-based visuals, like minecount, time,
    options.
    """

    def __init__(self, display_size, terrain):
        self.size = display_size
        self.terrain = terrain

        self.clock = time.Clock()
        self.time = {'m': 0, 's': 0.0}

        self.board_shown = False
        self.mouse_freed = False

        self.__render_options()


    def update_time(self):
        """ Record time user has spent playing. """

        self.clock.tick()

        if not self.terrain.playing:
            # Continue calling this function
            # so that when we start it again,
            # it does not jump to add a large
            # amount of time. This happens because
            # it returns the amount of time between
            # consecutive calls.
            self.clock.get_time()
            return

        self.time['s'] += self.clock.get_time()

        if self.time['s'] > 60000:
            self.time['m'] += 1
            self.time['s'] = 0.0


    def _render(self, text, font, color, bcolor=None):
        """ Return a surface on which text is rendered. """

        rendered = font.render(str(text), True, color, bcolor)
        return rendered


    def __render_options(self):
            """ Render surfaces of all option buttons. """

            restart = {
                's': self._render(
                    "Restart", SF[int(1 / 12 * DISPLAY_HEIGHT)],
                    (255, 255, 255), (0, 0, 0)
                )
            }
            restart['w'] = restart['s'].get_width()
            restart['c'] = (
                (self.size - restart['w']) / 2,
                1 / 5 * self.size
            )
            restart['r'] = restart['s'].get_rect(topleft=restart['c'])

            show_board = {
                's': self._render(
                    "Show board", SF[int(1 / 12 * DISPLAY_HEIGHT)],
                    (255, 255, 255), (0, 0, 0)
                )
            }
            show_board['w'] = show_board['s'].get_width()
            show_board['c'] = (
                (self.size - show_board['w']) / 2,
                3 / 5 * self.size
            )
            show_board['r'] = show_board['s'].get_rect(topleft=show_board['c'])

            escape = {
                's': self._render(
                    " Return ", SF[32], (0, 0, 0), (245, 245, 245)
                )
            }
            escape['w'] = escape['s'].get_width()
            escape['c'] = (
                (self.size - escape['w']) / 2,
                (TERRAIN_MARGIN - escape['s'].get_height()) / 2
            )
            escape['r'] = escape['s'].get_rect(topleft=escape['c'])

            self.options = {
                'r': restart,
                'b': show_board,
                'e': escape
            }


    def render_statbar(self, target):
        """ Blit all status bar elements to target. """

        ls = lambda x: len(str(x))

        time = self._render(
            '{0}{2}:{1}{3}'.format(
                # The replacements 0 and 1 are to add
                # leading zeroes to the clock seconds,
                # so it does not shift around
                '0' if ls(self.time['m']) < 2 else '',
                '0' if ls(int(self.time['s'] / 1000)) < 2 else '',
                self.time['m'], int(self.time['s'] / 1000)
            ),
            SF[32], (255, 255, 255)
        )

        stats = self.terrain.get_stats()
        mm = stats[2] - stats[3]

        marked = self._render(
            "Mines: {}{}".format(
                # Add space so it doesn't
                # constantly shift around
                ' ' * (2 - ls(mm)),
                mm,
            ),
            SF[32], (255, 255, 255)
        )

        height = (TERRAIN_MARGIN - time.get_height()) / 2

        target.blit(time, (1 / 5 * self.size, height))
        target.blit(
            marked, (4 / 5 * self.size - marked.get_width(), height)
        )


    def render_options(self, target):
        """ Blit all options to target, if player has
        won or lost. """

        if self.terrain.playing:
            return

        opt = self.options

        if self.board_shown:
            target.blit(opt['e']['s'], opt['e']['c'])
        else:
            target.blit(opt['r']['s'], opt['r']['c'])
            target.blit(opt['b']['s'], opt['b']['c'])


    def update_options(self, lmouse, mouse_pos):
        """ Check if user clicks on any option
        button, and react accordingly. """

        if self.terrain.playing:
            return

        if not self.mouse_freed:
            # Player has to free the mouse
            # once before he's able to click again
            if lmouse:
                return
            else:
                self.mouse_freed = True

        opt = self.options

        if self.terrain.playing:
            return

        if lmouse:
            for b in ('r', 'b', 'e'):
                if opt[b]['r'].collidepoint(mouse_pos):
                    if self.board_shown:
                        if b == 'e':
                            self.board_shown = False
                    else:
                        if b == 'r':
                            print("New game! Here we go!")
                            self.terrain.restart()
                            self.time['m'] = 0
                            self.time['s'] = 0.0
                            self.mouse_freed = False
                        if b == 'b':
                            self.board_shown = True
                          

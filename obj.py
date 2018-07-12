""" Objects for PySweeper. These are:
 - The Terrain (container for all the plots)
 - A Plot object that represents each individual plot
 - A manager that controls all other options
"""

# pylint: disable=no-member

from random import randrange, shuffle, choice

from pygame import font, surface, time

from const import (
    TERRAIN_MARGIN, PLOT_PADDING,
    PLOT_SIZE, PLOT_TILES,
    FONT_PATH, SCREEN_SIZE
)


# Font preloading
font.init()
SF = {}

STAT_SIZE = TERRAIN_MARGIN
TITLE_SIZE = int(1 / 8 * SCREEN_SIZE)

for size in (STAT_SIZE, TITLE_SIZE):
    SF[size] = font.Font(FONT_PATH, size)


class Terrain_Manager():
    """ God oject class that controls generation, allocation
    and management of the terrain and its plots.
    """

    def __init__(self, terrain_side):
        # Terrain side is the number of plots
        # along one side of the game terrain
        self.terrain_side = terrain_side
        self.plot_quantity = terrain_side ** 2


        self.has_clicked = False
        # 0 = playing, 1 = lost, 2 = won
        self.play_state = 0
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
        If minemap, print a map of all the mines.
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

        # If play_state is nonzero,
        # there's nothing to update
        if self.play_state:
            return

        for plot in self.plots:
            if not plot.revealed:
                if lmouse:
                    if plot.state == 0:
                        if plot.rect.collidepoint(mouse_pos):

                            if not self.has_clicked:
                                # Player can't die on first click.
                                # Clear plot and zone around it
                                # to make sure it's not
                                # impossible
                                self.clear_area(plot)
                                self.has_clicked = True


                            # Clicked on mined plot
                            if plot.type == 1:
                                plot.reveal(14)
                                print('You died!')
                                self.reveal_all()
                                self.play_state = 1
                                # Return so it doesn't
                                # repaint over
                                return

                            adjacent = self.get_adjacent_mines(plot)
                            if adjacent == 0:
                                # No adjacent mines, check further
                                self.reveal_adjacent_plots(plot)

                            # Reveal plot according to quantity
                            # of surrounding mines
                            plot.reveal(adjacent)

                elif rmouse:
                    if plot.rect.collidepoint(mouse_pos):
                        state = plot.toggle_state()
                        if state == 1:
                            self.marked_mines += 1
                        elif state == 2:
                            self.marked_mines -= 1

                    # Game can only be won from a right-click
                    self.check_victory()


    def clear_area(self, plot):
        """ Move a mine from a plot to another one.
        Only used once per game, if the player's first
        click is on a mine.
        """

        zone = [
            plot for plot in self.get_adjacent_plots(plot)
        ]
        # Don't omit clicked plot
        zone.append(plot)

        moved = 0

        for plot in zone:
            if plot.type == 1:
                moved += 1
                while True:
                    new_target = self.get_plot(
                        randrange(0, self.terrain_side),
                        randrange(0, self.terrain_side)
                    )
                    if (
                        new_target not in zone
                        and new_target.type == 0
                    ):
                        new_target.type = 1
                        plot.type = 0
                        break

        # print("Relocated {} mine{}".format(
        #     moved, 's' if moved != 1 else '')
        # )


    def get_adjacent_plots(self, plot):
        """ Return a list with all adjacent plots. """

        x = plot.x_offset
        y = plot.y_offset

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

        return len([
            plot for plot in
            self.get_adjacent_plots(plot)
            if plot.type == 1
        ])


    def get_plot(self, x_offset, y_offset):
        """ Returns the plot that matches the given x_offset
        and y_offset, returns None if none were found.
        """

        shift = (y_offset * self.terrain_side) + x_offset

        if (
            # Ensure the plot is the one we're after
            shift < self.plot_quantity
            and self.plots[shift].x_offset == x_offset
            and self.plots[shift].y_offset == y_offset
        ):
            return self.plots[shift]


    def reveal_adjacent_plots(self, plot):
        """ Reveal all adjacent plots, and those adjacent
        to them, until all plots are adjacent to mines.
        """

        adjacent_to = self.get_adjacent_plots
        adjacent_mines_to = self.get_adjacent_mines

        plot_queue = adjacent_to(plot)
        next_queue = []

        # Empty iterables are False (PEP8)
        while plot_queue:

            for plot in plot_queue:
                if not plot.revealed:

                    if adjacent_mines_to(plot) == 0:
                        plot.reveal(0)

                        for adj_plot in adjacent_to(plot):
                            if adj_plot not in next_queue:
                                next_queue.append(adj_plot)

                    else:
                        plot.reveal(adjacent_mines_to(plot))

            plot_queue = [
                plot for plot in next_queue if
                plot not in plot_queue
            ]
            next_queue = []


    def check_victory(self):
        """ Check if the player has won, by verifying that
        exclusively all plots with mines have been marked.
        """

        if self.marked_mines == self.mine_quantity:
            # If the player has marked all mines properly,
            # this should return True
            if all([
                plot.type for plot in self.plots
                if plot.state == 1
            ]):
                print('You did it!')
                self.play_state = 2
                self.reveal_all()


    def reveal_all(self):
        """ Unveil all the plots. """

        for plot in self.plots:
            if not plot.revealed:

                # If the plot had a mine
                if plot.type == 1:
                    # But was not marked
                    if plot.state == 0:
                        plot.reveal(11)
                    # But was marked
                    elif plot.state == 1:
                        plot.reveal(13)

                # If the plot was safe but was marked
                elif plot.type == 0 and plot.state == 1:
                    plot.reveal(12)
                else:
                    plot.reveal(self.get_adjacent_mines(plot))


    def restart(self):
        """ Restart new game. """
        self.has_clicked = False
        self.play_state = 0
        self.marked_mines = 0
        self.plots = []

        self.__generate_mine_map()
        self.__generate_plots()

        print(choice([
            "Here we go again!",
            "A new game brings new possibilities!",
            "Good luck!",
            "You can do it!",
            "And another one!",
            "There's just no stopping you, is there?",
            "GOGOGO!"
        ]))


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
        """ Reveal the contents of the plot by updating
        plot tile to display PLOT_TILES[tile].
        """
        self.revealed = True
        # The destination coordinates are relative to
        # the plot's surface.
        self.surface.blit(PLOT_TILES[tile], (0, 0))


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

        if not self.terrain.has_clicked:
            # Player hasn't begun playing
            return

        if self.terrain.play_state:
            # Not playing
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
        """ Return a surface on which `text` is rendered. """

        return font.render(str(text), True, color, bcolor)


    def __render_options(self):
            """ Render surfaces of all option buttons. """

            restart = {
                's': self._render(
                    "Restart", SF[TITLE_SIZE],
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
                    "Show board", SF[TITLE_SIZE],
                    (255, 255, 255), (0, 0, 0)
                )
            }
            show_board['w'] = show_board['s'].get_width()
            show_board['c'] = (
                (self.size - show_board['w']) / 2,
                3 / 5 * self.size
            )
            show_board['r'] = show_board['s'].get_rect(
                topleft=show_board['c']
            )

            defeat = {
                's': self._render(
                    "You lost!", SF[TITLE_SIZE],
                    (254, 0, 0), (0, 0, 0)
                )
            }
            defeat['w'] = defeat['s'].get_width()
            defeat['c'] = (
                (self.size - defeat['w']) / 2,
                2 / 5 * self.size
            )
            defeat['r'] = defeat['s'].get_rect(topleft=defeat['c'])

            victory = {
                's': self._render(
                    "You won!", SF[TITLE_SIZE],
                    (0, 200, 83), (0, 0, 0)
                )
            }
            victory['w'] = victory['s'].get_width()
            victory['c'] = (
                (self.size - victory['w']) / 2,
                2 / 5 * self.size
            )
            victory['r'] = victory['s'].get_rect(topleft=victory['c'])

            escape = {
                's': self._render(
                    " Return ", SF[STAT_SIZE],
                    (0, 0, 0), (245, 245, 245)
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
                'e': escape,
                'v': victory,
                'd': defeat
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
            SF[STAT_SIZE], (255, 255, 255)
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
            SF[STAT_SIZE], (255, 255, 255)
        )

        height = (TERRAIN_MARGIN - time.get_height()) / 2

        target.blit(time, (TERRAIN_MARGIN, height))
        target.blit(
            marked, (
                self.size
                - TERRAIN_MARGIN
                - marked.get_width(),
                height
            )
        )


    def render_options(self, target):
        """ Blit all options to target, if player has
        won or lost. """

        if not self.terrain.play_state:
            return

        opt = self.options

        if self.board_shown:
            target.blit(opt['e']['s'], opt['e']['c'])
        else:
            target.blit(opt['r']['s'], opt['r']['c'])
            target.blit(opt['b']['s'], opt['b']['c'])
            if self.terrain.play_state == 1:
                target.blit(opt['d']['s'], opt['d']['c'])
            else:
                target.blit(opt['v']['s'], opt['v']['c'])


    def update_options(self, lmouse, mouse_pos):
        """ Check if user clicks on any option
        button, and react accordingly. """

        if not self.terrain.play_state:
            return

        if not self.mouse_freed:
            # Player has to free the mouse
            # once before he's able to click again
            if lmouse:
                return
            else:
                self.mouse_freed = True

        opt = self.options

        if lmouse:
            for b in ('r', 'b', 'e'):
                if opt[b]['r'].collidepoint(mouse_pos):
                    if self.board_shown:
                        if b == 'e':
                            self.board_shown = False
                    else:
                        if b == 'r':
                            self.terrain.restart()
                            self.time['m'] = 0
                            self.time['s'] = 0.0
                            self.mouse_freed = False
                        if b == 'b':
                            self.board_shown = True

import pygame
from pygame.locals import *



from obj import Terrain, Plot

from const import PLOT_PADDING, PLOT_SIZE, TERRAIN_MARGIN



def get_side():
    is_answer_gotten = False
    while not is_answer_gotten:
        try:
            size = int(input(
                "How long do you want your terrain side to be?\n"
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


# print("Welcome to Python Minesweeper!")
# print("Please pick a terrain size, between 5 and 16")

terrain_side = get_side()

# print("Your terrain will be {0}x{0}".format(terrain_side))

# Generate display size : PLOT_SIZE per plot
# PLOT_PADDING between them
# TERRAIN_MARGIN on each side
screen_size = (
    (PLOT_SIZE * terrain_side)
    + PLOT_PADDING * (terrain_side - 2)
    + TERRAIN_MARGIN * 2
)

terrain = Terrain(terrain_side)
print(terrain.get_stats())




pygame.init()
display = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("PySweeper")

is_mouse_left_click = False
is_mouse_right_click = False

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type == MOUSEBUTTONDOWN:
            # Use elif because we only want one button to be
            # registered at a time
            if event.button == 1:
                is_mouse_left_click = True
            elif event.button == 3:
                is_mouse_right_click = True

        if event.type == MOUSEBUTTONUP:
            # User has lifted mouse buttons
            # Allow mouse press events back into the queue
            pygame.event.set_allowed(MOUSEBUTTONDOWN)
            if event.button == 1:
                is_mouse_left_click = False
            if event.button == 3:
                is_mouse_right_click = False


    terrain.update_plots(
        is_mouse_left_click,
        is_mouse_right_click,
        pygame.mouse.get_pos()
    )

    # Place this after plot updating.
    # This forces the user to unpress the
    # mouse before being able to press again
    # It works by blocking mouse presses
    # from entering the event queue
    if is_mouse_right_click or is_mouse_left_click:
        pygame.event.set_blocked(MOUSEBUTTONDOWN)
        is_mouse_right_click = False
        is_mouse_left_click = False


    # Render queue
    # Highest last

    display.fill((10, 10, 10))
    terrain.render_plots(display)
    pygame.display.update()

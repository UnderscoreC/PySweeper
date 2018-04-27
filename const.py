""" Global constants for PySweeper.
You are free to edit (some of) these.
"""

from os import path, system, name

from pygame import image, transform, display

from function import request_size

# You can customize these

PLOT_SIZE = 55
PLOT_PADDING = 2


## Don't touch these

check = (
    PLOT_SIZE > 0,
    PLOT_PADDING >= 0,
)

try:
    assert all(check)
except AssertionError:
    raise AssertionError('All values in const.py must be positive!')

# Path generation

ROOT_PATH = path.dirname(__file__)
RESOURCE_PATH = path.join(ROOT_PATH, 'res')
IMAGE_PATH = path.join(RESOURCE_PATH, 'img')
FONT_PATH = path.join(RESOURCE_PATH, 'sfm.otf')

# Image preloading

PLOT_TILES = {}

for number in range(15):
    pil = image.load
    pis = transform.smoothscale

    PLOT_TILES[number] = pis(
        pil(path.join(IMAGE_PATH, '{}.png'.format(number))),
        (PLOT_SIZE, PLOT_SIZE)
    )

ICON = image.load(path.join(IMAGE_PATH, 'icon.png'))

# Clear png_read_image errors
system('cls' if name == 'nt' else 'clear')


# Size generation

TERRAIN_SIDE = request_size(9, 64)

# Generate display size : PLOT_SIZE per plot
# PLOT_PADDING between them
# TERRAIN_MARGIN on each side
SCREEN_SIZE = (
    (PLOT_SIZE * TERRAIN_SIDE)
    + PLOT_PADDING * (TERRAIN_SIDE - 2)
)

TERRAIN_MARGIN = int(1 / 10 * SCREEN_SIZE)
TERRAIN_MARGIN = 40 if TERRAIN_MARGIN > 40 else TERRAIN_MARGIN

# Add a margin to the screen
SCREEN_SIZE += 2 * TERRAIN_MARGIN

# Get display height
display.init()
DISPLAY_HEIGHT = display.Info().current_h

# Check and warn user if SCREEN_SIZE
# is taller than display
if SCREEN_SIZE > DISPLAY_HEIGHT:
    print(
        "Warning: game terrain taller than "
        "screen height. The entire board will "
        "not fit. Modify values in const.py "
        "to resize."
    )

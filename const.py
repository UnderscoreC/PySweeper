""" Global constants for PySweeper.
You are free to edit (some of) these.
"""

from os import path, system, name

from pygame import image, transform, display

# You can customize these

PLOT_SIZE = 60
PLOT_PADDING = 0
# Terrain margin min = 30
TERRAIN_MARGIN = 30


## Don't touch these

check = (
    PLOT_SIZE > 0,
    PLOT_PADDING >= 0,
)

try:
    assert all(check)
except AssertionError:
    raise AssertionError('All values in const.py must be positive!')

TERRAIN_MARGIN = TERRAIN_MARGIN if TERRAIN_MARGIN >= 30 else 30

# Path generation

ROOT_PATH = path.dirname(__file__)
RESOURCE_PATH = path.join(ROOT_PATH, 'res')
IMAGE_PATH = path.join(RESOURCE_PATH, 'img')

# Get display height
display.init()
DISPLAY_HEIGHT = display.Info().current_h

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

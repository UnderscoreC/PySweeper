""" Universal constants for PySweeper.
You are free to edit (some of) these.
"""

from os import path

from pygame import image, transform


# Max recommended value: 60
PLOT_SIZE = 60
PLOT_PADDING = 3
TERRAIN_MARGIN = 20

## Don't touch these

ROOT_PATH = path.dirname(__file__)
# RESOURCE_PATH = path.join(ROOT_PATH, 'res')
IMAGE_PATH = path.join(ROOT_PATH, 'res', 'img')

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

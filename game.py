# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField
from glazov import GlazovDrone


if __name__ == '__main__':
    scene = SpaceField(
        speed=7,
        asteroids_count=5,
    )
    for x in range(5):

        x = GlazovDrone()


    scene.go()

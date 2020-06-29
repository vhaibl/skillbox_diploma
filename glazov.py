# -*- coding: utf-8 -*-
import random

from astrobox.core import Drone


class GlazovDrone(Drone):
    my_team = []

    def __init__(self):
        super().__init__()
        self.used = []

    def on_born(self):
        self.target = self._get_my_asteroid()
        self.move_at(self.target)
        self.my_team.append(self)

    def _get_my_asteroid(self):
        asteroids = self.asteroids
        for delete in self.used:
            asteroids.remove(delete)
        if len(asteroids) == 0:
            return self.my_mothership
        asteroid = random.choice(asteroids)
        self.used.append(asteroid)
        return asteroid

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if self.payload < 100 and self.target.payload <= 0:
            self.target = self._get_my_asteroid()
            self.move_at(self.target)
        else:
            self.move_at(self.my_mothership)

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):
        self.if_empty()

    def on_wake_up(self):
        self.target = self._get_my_asteroid()
        if self.target:
            self.move_at(self.target)

    def if_empty(self):
        # TODO - Нейминг! Имя функции не отражает её суть. Функция это прежде всего глагол
        if self.target.payload <= 0:
            self.target = self._get_my_asteroid()
        self.move_at(self.target)

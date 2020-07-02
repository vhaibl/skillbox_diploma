# -*- coding: utf-8 -*-
import random

from astrobox.core import Drone


class GlazovDrone(Drone):
    my_team = []

    def __init__(self):
        super().__init__()
        self.used = set()
        # self.part_loaded1 = {}
        # self.empty1 = {}
        # self.full_loaded1 = {}
        # self.part_loaded1[self.id] = 0
        # self.empty1[self.id] = 0
        # self.full_loaded1[self.id] = 0
        self.stats_dict = {}
        self.stats_dict[self.id] = {}
        # self.stats_dict[self.id]['empty'] = 0
        # self.stats_dict[self.id]['partial'] = 0
        # self.stats_dict[self.id]['full'] = 0

    def stats(func, *args, **kwargs):
        def surrogate(self, *args, **kwargs):

            result = func(self, *args, **kwargs)
            if 'empty' not in self.stats_dict[self.id]:
                self.stats_dict[self.id]['empty'] = 0
                self.stats_dict[self.id]['partial'] = 0
                self.stats_dict[self.id]['full'] = 0
            if self.is_empty:
                self.stats_dict[self.id]['empty'] += int(self.distance_to(self.target))
            if self.free_space > 0 and self.free_space < 100:
                self.stats_dict[self.id]['partial'] += int(self.distance_to(self.target))
            if self.fullness == 1:
                self.stats_dict[self.id]['full'] += int(self.distance_to(self.target))
            return result

        return surrogate

    @stats
    def on_born(self):
        self.my_team.append(self)

        if self.id == 1:
            self.target = self._get_my_asteroid(dist='distance_far')
        elif self.id == 2:
            self.target = self._get_my_asteroid(dist='distance_far')
        else:
            self.target = self._get_my_asteroid(dist='distance_random')

        # self.stats()

        self.move_at(self.target)
        self.my_team.append(self)

    # @stats
    def _get_my_asteroid(self, dist):
        asteroids = self.asteroids

        for delete in self.used:
            if delete.payload == 0:
                if delete in asteroids:
                    asteroids.remove(delete)

        def max_distance():
            max = 0
            target = None
            for a in asteroids:
                if self.distance_to(a) > max:
                    max = self.distance_to(a)
                    target = a
            return target

        def min_distance():
            min = 100000
            target = None
            for a in asteroids:
                if self.distance_to(a) < min:
                    min = self.distance_to(a)
                    target = a
            return target

        def avg_distance():
            distance_list = []
            for a in asteroids:
                distance_list.append((self.distance_to(a), a))
            distance_list = sorted(reversed(distance_list))
            z = (len(distance_list) // 2)
            avg = distance_list[z][1]
            return avg

        def rand_distance():
            distance_list = []
            for a in asteroids:
                distance_list.append((self.distance_to(a), a))
            distance_list = sorted(reversed(distance_list))
            z = random.randint(0, len(distance_list) - 1)
            rand = distance_list[z][1]
            return rand

        if len(asteroids) == 0:
            return self.my_mothership

        if dist == 'distance_far':
            asteroid = max_distance()
        elif dist == 'distance_near':
            asteroid = min_distance()
        elif dist == 'distance_average':
            asteroid = avg_distance()
        elif dist == 'distance_random':
            asteroid = rand_distance()
        self.used.add(asteroid)

        return asteroid

    @stats
    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    @stats
    def on_load_complete(self):
        if self.payload < 30 and self.target.payload <= 0:
            while self.target.payload == 0:
                self.target = self._get_my_asteroid(dist='distance_near')
            # self.stats()
            self.move_at(self.target)

        else:
            # self.stats()
            self.move_at(self.my_mothership)

    @stats
    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    @stats
    def on_unload_complete(self):
        self.if_empty()

        while self.target.payload == 0:
            self.target = self._get_my_asteroid(dist='distance_random')

        # self.stats()
        self.move_at(self.target)
        print(
            f'Дрон {self.id} пролетел {self.stats_dict[self.id]["empty"]} ед. пустым, '
            f'{self.stats_dict[self.id]["partial"]} ед. частично загруженным,'
            f' {self.stats_dict[self.id]["full"]} ед. полностью загруженным')

    @stats
    def on_wake_up(self):
        # self.stats()
        pass

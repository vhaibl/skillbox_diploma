# -*- coding: utf-8 -*-
import random

from astrobox.core import Drone


class GlazovDrone(Drone):
    my_team = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.used = set()
        self.stats_dict = {}
        self.stats_dict[self.id] = {}

    def stats(self):
        if 'empty' not in self.stats_dict[self.id]:
            self.stats_dict[self.id]['empty'] = 0
            self.stats_dict[self.id]['partial'] = 0
            self.stats_dict[self.id]['full'] = 0
        if self.is_empty:
            self.stats_dict[self.id]['empty'] += int(self.distance_to(self.target))
        if self.free_space > 0 and self.free_space < 100:
            self.stats_dict[self.id]['partial'] += int(self.distance_to(self.target))
        if self.is_full:
            self.stats_dict[self.id]['full'] += int(self.distance_to(self.my_mothership))
        return self.stats_dict

    def on_born(self):
        self.my_team.append(self)

        if self.id == 1:
            self.target = self._get_my_asteroid(dist='distance_near')
        elif self.id == 2:
            self.target = self._get_my_asteroid(dist='distance_near')
        else:
            self.target = self._get_my_asteroid(dist='distance_random')
        self.move_at(self.target)
        self.my_team.append(self)

    def __max_distance(self, asteroids):
        # TODO - Нейминг! Переменная имеет имя как ключевое слово python. Теперь она перекрывает его
        max = 0
        target = None
        for asteroid in asteroids:
            if self.distance_to(asteroid) > max:
                max = self.distance_to(asteroid)
                target = asteroid
        return target

    def __min_distance(self, asteroids):
        # TODO - Нейминг! Переменная имеет имя как ключевое слово python. Теперь она перекрывает его
        min = 100000
        target = None
        for asteroid in asteroids:
            if self.distance_to(asteroid) < min:
                min = self.distance_to(asteroid)
                target = asteroid
        return target

    def __avg_distance(self, asteroids):
        distance_list = []
        for asteroid in asteroids:
            distance_list.append((self.distance_to(asteroid), asteroid))
        distance_list = sorted(distance_list)
        # TODO - Нейминг! Однобуквенные переменные - плохой тон
        z = (len(distance_list) // 2)
        avg = distance_list[z][1]
        return avg

    def __rand_distance(self, asteroids):
        distance_list = []
        for asteroid in asteroids:
            distance_list.append((self.distance_to(asteroid), asteroid))
        if len(distance_list) >= 6:
            distance_list = sorted(distance_list[0:len(distance_list)//2-5])
        else:
            distance_list = sorted(distance_list[0:len(distance_list)])
        # TODO - Нейминг! Однобуквенные переменные - плохой тон
        z = random.randint(0, len(distance_list) - 1)
        rand = distance_list[z][1]
        return rand

    def _get_my_asteroid(self, dist):
        asteroids = self.asteroids
        for delete in self.used:
            if delete in asteroids:
                asteroids.remove(delete)
        if len(asteroids) == 0:
            return self.my_mothership
        if dist == 'distance_far':
            asteroid = self.__max_distance(asteroids)
        elif dist == 'distance_near':
            asteroid = self.__min_distance(asteroids)
        elif dist == 'distance_average':
            asteroid = self.__avg_distance(asteroids)
        elif dist == 'distance_random':
            asteroid = self.__rand_distance(asteroids)
        else:
            asteroid = self.__rand_distance(asteroids)
        self.used.add(asteroid)
        return asteroid

    def move_at(self, target, speed=None):
        if not self.is_alive:
            return
        self.stats()
        super().move_at(target, speed=speed)
        if self.target == self.my_mothership and self.is_empty:
            print(
                f'Дрон {self.id} пролетел {self.stats_dict[self.id]["empty"]} ед. пустым, '
                f'{self.stats_dict[self.id]["partial"]} ед. частично загруженным,'
                f' {self.stats_dict[self.id]["full"]} ед. полностью загруженным')

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if self.payload < 90 and self.target.payload <= 0:
            while self.target.payload == 0:
                self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)
        else:
            self.move_at(self.my_mothership)

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):
        while self.target.payload == 0:
            if self.id == 1 or self.id == 2 or self.id:
                self.target = self._get_my_asteroid(dist='distance_near')
            else:
                self.target = self._get_my_asteroid(dist='distance_random')
        self.move_at(self.target)

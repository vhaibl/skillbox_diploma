# -*- coding: utf-8 -*-
import random

from astrobox.core import Drone


class GlazovDrone(Drone):
    my_team = []

    def __init__(self):
        # TODO - Перед использованием функции супер-класса неплохо было бы посмотреть аргументы её.
        #  Там кварги передаются
        super().__init__()
        self.used = set()
        # TODO - Почистите код от закомментированного кода. Если понадобится, вытащите из коммитов
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

    def stats_decorator(func):
        # TODO - Эта функция не используется, убирайте

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

    def stats(self):
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
        return self.stats_dict

    def on_born(self):
        self.my_team.append(self)

        if self.id == 1:
            self.target = self._get_my_asteroid(dist='distance_far')
        elif self.id == 2:
            self.target = self._get_my_asteroid(dist='distance_far')
        else:
            self.target = self._get_my_asteroid(dist='distance_random')
        self.move_at(self.target)
        self.my_team.append(self)

    def _get_my_asteroid(self, dist):
        asteroids = self.asteroids
        for delete in self.used:
            if delete in asteroids:
                asteroids.remove(delete)

        # TODO - Не делайте так никогда: определение функция внутри др функции
        #  лучше сделайте приватным методом класса
        def max_distance():
            max = 0
            target = None
            # TODO - Нейминг! Однобуквенные переменные - плохой тон.
            #  Чтобы понять для чего эта переменная, нужно проанализировать код ниже, понять суть её, затем вернуться
            #  и продолжить анализ кода
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
            return self.mothership

        if dist == 'distance_far':
            asteroid = max_distance()
        elif dist == 'distance_near':
            asteroid = min_distance()
        elif dist == 'distance_average':
            asteroid = avg_distance()
        elif dist == 'distance_random':
            asteroid = rand_distance()
        # TODO - PyCharm подсказывает, что asteroid не всегда м.б. определена ,что вызовет ошибку при таком случае
        self.used.add(asteroid)

        return asteroid

    def move_at(self, target, speed=None):
        if not self.is_alive:
            return
        self.stats()
        super().move_at(target, speed=speed)

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if self.payload < 50 and self.target.payload <= 0:
            while self.target.payload == 0:
                self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)
        else:
            self.move_at(self.my_mothership)

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):
        while self.target.payload <= 1:
            self.target = self._get_my_asteroid(dist='distance_random')
        self.move_at(self.target)
        if self.target is self.mothership:
            print(
                f'Дрон {self.id} пролетел {self.stats_dict[self.id]["empty"]} ед. пустым, '
                f'{self.stats_dict[self.id]["partial"]} ед. частично загруженным,'
                f' {self.stats_dict[self.id]["full"]} ед. полностью загруженным')

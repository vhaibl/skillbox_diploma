# -*- coding: utf-8 -*-
import random
from abc import ABC, abstractmethod

from astrobox.core import Drone
from robogame_engine import GameObject
from robogame_engine.geometry import Point, Vector
from robogame_engine.theme import theme




class Drones(Drone, ABC):
    my_team = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.used = set()
        self.stats_dict = {}
        self.stats_dict[self.id] = {}
        self.condition = 'normal'
        self.target = None
        self.destination = None
        self.ready = False
        self.destinations = {
            1: (random.randint(120, theme.FIELD_WIDTH - 120), random.randint(120, theme.FIELD_HEIGHT - 120)),
            2: (random.randint(120, theme.FIELD_WIDTH - 120), random.randint(120, theme.FIELD_HEIGHT - 120)),
            3: (random.randint(120, theme.FIELD_WIDTH - 120), random.randint(120, theme.FIELD_HEIGHT - 120)),
            4: (random.randint(120, theme.FIELD_WIDTH - 120), random.randint(120, theme.FIELD_HEIGHT - 120)),
            5: (random.randint(120, theme.FIELD_WIDTH - 120), random.randint(120, theme.FIELD_HEIGHT - 120))}

        if self.id == 1:
            self.job = 'worker'
        else:
            self.job = 'fighter'
        self.bornt = 0
    @abstractmethod
    def on_born(self):

        pass

    def turn_to(self, target, speed=None):
        super().turn_to(target, speed=speed)

    def on_hearbeat(self):
        if self.health <= 66:
            self.go_healing()

        elif self.health >= 95 and self.condition == 'wounded':
            self.return_after_healing()

    def return_after_healing(self):
        self.condition = 'normal'
        self.destination = None
        self.target = None
        if self.job == 'worker':
            if self.payload < 90:
                self.destination = self._get_my_asteroid(dist='distance_near')
            else:
                self.destination = self.my_mothership
            self.move_at(self.destination)
        if self.job == 'fighter':
            self.destination = None
            self.target = None

    def go_healing(self):
        self.condition = 'wounded'
        self.destination = self.my_mothership
        if str(self.coord) != str(self.destination):
            self.move_at(self.destination)

    def move_at(self, target, speed=None):
        if not self.is_alive:
            return
        self.stats()
        super().move_at(target, speed=speed)
        if self.target == self.my_mothership and self.is_empty and self.job is 'worker':
            print(
                f'Дрон {self.id} пролетел {self.stats_dict[self.id]["empty"]} ед. пустым, '
                f'{self.stats_dict[self.id]["partial"]} ед. частично загруженным,'
                f' {self.stats_dict[self.id]["full"]} ед. полностью загруженным')

    def stats(self):
        if isinstance(self.target, GameObject):
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





class Fighter(Drones):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_born(self):
        self.my_team.append(self)
        self.start_destination = Point(self.destinations[self.id][0], self.destinations[self.id][1])
        self.move_at(self.start_destination)



    def on_hearbeat(self):
        if str(self.start_destination) == str(self.coord) and not self.ready and self.job == 'fighter':
            self.destination = None
            self.target = None
            self.ready = True

        elif self.job == 'fighter' and self.condition == 'normal' and self.ready:
            self.fighter_get_target_move_and_attack()

    def get_target(self):
        enemies = [(drone, self.distance_to(drone), drone.id) for drone in self.scene.drones if
                   self.team != drone.team and drone.is_alive]

        bases = [(base, self.distance_to(base)) for base in self.scene.motherships if
                 base.team != self.team and base.is_alive]
        bases.sort(key=lambda x: x[1])
        enemies.sort(key=lambda x: x[2])

        basa = None
        enemy = None
        # TODO - Попробуйте попрактиковать паттерн Стратегия
        #  https://refactoring.guru/ru/design-patterns/strategy/python/example
        #  Предпосылки: в зависимости от строковой переменной self.job логика принятия решений в ключевых
        #  точках раздваивается с помощью if. Было бы удобнее принимать стратегические решения, отдавая
        #  детали реализации в текущую стратегию
        if len(enemies) > 0:
            if self.job == 'fighter':
                chosen_one = enemies[0]
                enemy = chosen_one[0]

        if len(bases) > 0:
            if self.job == 'fighter':
                chosen_one = bases[0]
                basa = chosen_one[0]

        if len(enemies) <= 1 and len(bases) >= 1:
            self.target = basa
            if self.id == 1:
                self.job = 'worker'
            return self.target
        elif len(enemies) > 0 and len(bases) == 0:
            self.target = enemy
            if self.id == 2:
                self.job = 'worker'
            return self.target
        elif len(enemies) == 0 and len(bases) == 0:
            self.job = 'worker'
            self.target = self.my_mothership
            return self.target

        else:
            self.target = enemy
            return self.target

    def fighter_get_target_move_and_attack(self):
        if not self.target or not self.target.is_alive: self.target = self.get_target()
        if not self.destination: self.destination = self.get_place_for_attack(self, self.target)
        if str(self.coord) != str(self.destination):
            self.move_at(self.destination)

        elif self.distance_to(self.target) > 580:
            self.destination = None
        else:
            self.fighter_attack()
        if hasattr(self.target, 'is_alive'):
            if not self.target.is_alive:
                self.target = None
                self.destination = None
        else:
            self.destination = None

    def fighter_attack(self):
        if str(self.coord) != str(self.destination):
            self.move_at(self.destination)
        if self.distance_to(self.my_mothership) > 120:
            self.vector = Vector.from_points(point1=self.coord, point2=self.target.coord)
            self.turn_to(self.target)
            self.gun.shot(self.target)

        else:
            self.destination = None

    def get_place_for_attack(self, soldier, target):

        if isinstance(target, GameObject):
            vec = Vector.from_points(target.coord, soldier.coord)
        elif isinstance(target, Point):
            vec = Vector.from_points(target, soldier.coord)
        else:
            raise Exception("target must be GameObject or Point!".format(target, ))

        dist = vec.module
        _koef = 1 / dist
        norm_vec = Vector(vec.x * _koef, vec.y * _koef)
        vec_gunshot = norm_vec * min(580, int(dist))
        purpose = Point(target.coord.x + vec_gunshot.x, target.coord.y + vec_gunshot.y)
        angles = [0, 60, -60, 30, -30]
        random.shuffle(angles)
        for ang in angles:
            place = self.get_place_near(purpose, target, ang)
            if place and soldier.valide_place(place):
                return place
        return None

    def get_place_near(self, point, target, angle):
        vec = Vector(point.x - target.x, point.y - target.y)
        vec.rotate(angle)
        return Point(target.x + vec.x, target.y + vec.y)

    def valide_place(self, point: Point):
        is_valide = 60 < point.x < theme.FIELD_WIDTH - 60 and 60 < point.y < theme.FIELD_HEIGHT - 60
        for partner in self.my_team:
            if not partner.is_alive or partner is self:
                continue
            is_valide = is_valide and (partner.distance_to(point) >= 60)
        return is_valide


class Worker(Drones):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_born(self):
        self.my_team.append(self)
        self.start_destination = Point(self.destinations[self.id][0], self.destinations[self.id][1])
        self.destination = self._get_my_asteroid(dist='distance_near')
        self.move_at(self.destination)


    def on_heartbeat(self):

        if  self.bornt == 0:
            self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)
            self.bornt = 1

    def on_wake_up(self):
        if self.payload < 90 and self.target.payload < 1:
            self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if hasattr(self.target, 'payload'):
            if self.payload < 90 and self.target.payload <= 0:
                while self.target.payload == 0:
                    self.target = self._get_my_asteroid(dist='distance_near')
                self.move_at(self.target)
            else:
                self.move_at(self.my_mothership)
        self.move_at(self.my_mothership)

    def on_stop_at_mothership(self, mothership):
        if mothership == self.my_mothership:
            self.unload_to(mothership)
        elif mothership != self.my_mothership:
            self.load_from(mothership)

    def on_unload_complete(self):
        if hasattr(self.target, 'payload'):
            while self.target.payload == 0 and self.target is not self.my_mothership:
                self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)
        else:
            self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)

    def _get_my_asteroid(self, dist):

        not_empty_asteroids = [asteroid for asteroid in self.scene.asteroids if not asteroid.is_empty]
        not_empty_asteroids.extend([mothership for mothership in self.scene.motherships
                                    if not mothership.is_alive and not mothership.is_empty])

        for delete in self.used:
            if delete in not_empty_asteroids:
                not_empty_asteroids.remove(delete)

        if len(not_empty_asteroids) == 0:
            return self.my_mothership

        if dist == 'distance_far':
            asteroid = self.__max_distance(not_empty_asteroids)
        elif dist == 'distance_near':
            asteroid = self.__min_distance(not_empty_asteroids)
        elif dist == 'distance_average':
            asteroid = self.__avg_distance(not_empty_asteroids)
        elif dist == 'distance_random':
            asteroid = self.__rand_distance(not_empty_asteroids)

        else:
            asteroid = self.__rand_distance(not_empty_asteroids)
        self.used.add(asteroid)
        return asteroid

    def __max_distance(self, not_empty_asteroids):
        max_distance = 0
        target = None
        for asteroid in not_empty_asteroids:
            if asteroid.payload > 0 and self.distance_to(asteroid) > max_distance:
                max_distance = self.distance_to(asteroid)
                target = asteroid
        return target

    def __min_distance(self, not_empty_asteroids):
        min_distance = 100000
        target = None
        for asteroid in not_empty_asteroids:
            if self.distance_to(asteroid) < min_distance:
                min_distance = self.distance_to(asteroid)
                target = asteroid
        return target

    def __avg_distance(self, not_empty_asteroids):
        distance_list = []
        for asteroid in not_empty_asteroids:
            distance_list.append((self.distance_to(asteroid), asteroid))
        distance_list = sorted(distance_list)
        half_length = (len(distance_list) // 2)
        avg = distance_list[half_length][1]
        return avg

    def __rand_distance(self, not_empty_asteroids):
        distance_list = []
        for asteroid in not_empty_asteroids:
            distance_list.append((self.distance_to(asteroid), asteroid))
        asteroids_count = len(self.asteroids)

        if len(distance_list) >= asteroids_count + 1:
            distance_list = sorted(distance_list[0:len(distance_list) // 2 - asteroids_count])
        else:
            distance_list = sorted(distance_list[0:len(distance_list)])
        random_asteroid = random.randint(0, len(distance_list) - 1)
        rand = distance_list[random_asteroid][1]
        return rand


class GlazovDrone(ABC):
    my_drones = []
    #TODO Я совсем не понимаю как воспользоваться паттерном стратегия. Я создал классы отдельные классы стратегий для
    #TODO Worker и Fighter, оставил одну с общими действиями, а как ими пользоваться? Как их переключать, после того как
    #TODO Figher отработает и должен стать Worker?
    #TODO Если стратегия Fighter, должны ли например в методе on_born сначала отрадотать команды из родительского
    #TODO класса, а потом из Fighter?

    def __init__(self):
        print(self.my_drones)

        self.soldier = Fighter()
        if self.soldier.job == 'fighter':
            print(self.soldier.job, self.soldier.id)
        if self.soldier.job == 'worker':
            print(self.soldier.job)
        self.my_drones.append(self)

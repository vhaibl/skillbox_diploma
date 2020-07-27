# -*- coding: utf-8 -*-
import math
import random
from abc import abstractmethod

from astrobox.core import Drone
from robogame_engine import GameObject
from robogame_engine.geometry import Point, Vector
from robogame_engine.theme import theme


class GlazovDrone(Drone):
    my_team = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job = None
        self.bornt = 0
        self.gun_range = 600
        self.used = set()
        self.stats_dict = {}
        self.stats_dict[self.id] = {}
        self.condition = 'normal'
        self.target = None
        self.destination = None
        self.ready = False
        self.no_enemies = False
        self.destinations = {
            1: {'x': 0, 'y': 140},
            2: {'x': 180, 'y': 65},
            3: {'x': 140, 'y': 140},
            4: {'x': 70, 'y': 140},
            5: {'x': 180, 'y': -15}}

    def on_born(self):
        self.my_team.append(self)
        self.my_number = len(self.my_team)
        if self.my_mothership.coord.x <= 100 and self.my_mothership.coord.y <= 100:
            self.start_destination = Point(self.my_mothership.coord.x + self.destinations[self.my_number]['x'],
                                           self.my_mothership.coord.y + self.destinations[self.my_number]['y'])
        if self.my_mothership.coord.x <= 100 and self.my_mothership.coord.y > 100:
            self.start_destination = Point(self.my_mothership.coord.x + self.destinations[self.my_number]['x'],
                                           self.my_mothership.coord.y - self.destinations[self.my_number]['y'])
        if self.my_mothership.coord.x > 100 and self.my_mothership.coord.y <= 100:
            self.start_destination = Point(self.my_mothership.coord.x - self.destinations[self.my_number]['x'],
                                           self.my_mothership.coord.y + self.destinations[self.my_number]['y'])
        if self.my_mothership.coord.x > 100 and self.my_mothership.coord.y > 100:
            self.start_destination = Point(self.my_mothership.coord.x - self.destinations[self.my_number]['x'],
                                           self.my_mothership.coord.y - self.destinations[self.my_number]['y'])

        if self.my_number == 1:
            self.job = Worker(self)
        else:
            self.job = Fighter(self)

        self.job.after_born()

    def on_hearbeat(self):
        if self.no_enemies:
            self.job = Worker(self)

        if self.health <= 66:
            self.go_healing()

        elif self.health >= 95 and self.condition == 'wounded':
            self.job.return_after_healing()

        self.job.doing_heartbeat()

    def go_healing(self):
        self.condition = 'wounded'
        self.job.destination = self.my_mothership
        if str(self.coord) != str(self.job.destination):
            self.move_at(self.job.destination)

    # TODO - В on_методах реализуем логику общую для всех типов или просто self.next_action()
    #  или же что-то значимое действие и дальше self.job.next_action()
    def on_wake_up(self):
        pass

    def on_stop_at_asteroid(self, asteroid):
        self.job.on_stop_at_asteroid(asteroid)

    def on_load_complete(self):
        self.job.on_load_complete()

    def on_stop_at_mothership(self, mothership):
        self.job.on_stop_at_mothership(mothership)

    def on_unload_complete(self):
        self.job.next_action()

    def move_at(self, target, speed=None):
        self.stats()
        super().move_at(target, speed=speed)
        if self.target == self.my_mothership and self.is_empty and self.job == Worker(self):
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


class Worker(GlazovDrone):

    def __init__(self, unit: GlazovDrone):
        self.unit = unit
        self.bornt = 0
        self.start_destination = self.unit.start_destination
        self.enemy_count = 0

    def _get_my_asteroid(self, dist):
        soldier = self.unit
        not_empty_asteroids = [asteroid for asteroid in soldier.scene.asteroids if not asteroid.is_empty]
        not_empty_asteroids.extend([mothership for mothership in soldier.scene.motherships
                                    if not mothership.is_alive and not mothership.is_empty])

        for delete in self.unit.used:
            if delete in not_empty_asteroids:
                not_empty_asteroids.remove(delete)

        if len(not_empty_asteroids) == 0:
            return soldier.my_mothership

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
        self.unit.used.add(asteroid)
        return asteroid

    def next_action(self):
        pass


    def after_born(self):
        self.unit.destination = self._get_my_asteroid(dist='distance_near')
        self.unit.move_at(self.unit.destination)
        return self.start_destination

    def return_after_healing(self):
        soldier = self.unit
        soldier.condition = 'normal'
        soldier.destination = None
        soldier.target = None
        if soldier.payload < 90:
            soldier.destination = self._get_my_asteroid(dist='distance_near')
        else:
            soldier.destination = soldier.my_mothership
        soldier.move_at(soldier.destination)

    def on_wake_up(self):
        soldier = self.unit
        if soldier.payload < 90 and soldier.target.payload < 1:
            soldier.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(soldier.target)

    def on_stop_at_asteroid(self, asteroid):
        self.unit.load_from(asteroid)

    def on_stop_at_mothership(self, mothership):
        if mothership == self.unit.my_mothership:
            self.unit.unload_to(mothership)
        elif mothership != self.unit.my_mothership:
            self.unit.load_from(mothership)

    def on_unload_complete(self):
        soldier = self.unit
        if hasattr(soldier.target, 'payload'):
            while soldier.target.payload == 0 and soldier.target is not soldier.my_mothership:
                soldier.target = self._get_my_asteroid(dist='distance_near')
            soldier.move_at(soldier.target)
        else:
            soldier.target = self._get_my_asteroid(dist='distance_near')
            soldier.move_at(soldier.target)

    def on_load_complete(self):
        soldier = self.unit

        if hasattr(soldier.target, 'payload'):
            if soldier.payload < 90 and soldier.target.payload <= 0:
                while soldier.target.payload == 0:
                    soldier.target = self._get_my_asteroid(dist='distance_near')
                soldier.move_at(soldier.target)
            else:
                soldier.move_at(soldier.my_mothership)
        soldier.move_at(soldier.my_mothership)

    def doing_heartbeat(self):

        if self.unit.bornt == 0:
            self.unit.target = self._get_my_asteroid(dist='distance_near')
            self.unit.move_at(self.unit.target)
            self.unit.bornt = 1

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
            if self.unit.distance_to(asteroid) < min_distance:
                min_distance = self.unit.distance_to(asteroid)
                target = asteroid

        return target

    def __avg_distance(self, not_empty_asteroids):
        distance_list = []
        for asteroid in not_empty_asteroids:
            distance_list.append((self.unit.distance_to(asteroid), asteroid))
        distance_list = sorted(distance_list)
        half_length = (len(distance_list) // 2)
        avg = distance_list[half_length][1]
        return avg

    def __rand_distance(self, not_empty_asteroids):
        distance_list = []
        for asteroid in not_empty_asteroids:
            distance_list.append((self.unit.distance_to(asteroid), asteroid))
        asteroids_count = len(self.unit.asteroids)

        if len(distance_list) >= asteroids_count + 1:
            distance_list = sorted(distance_list[0:len(distance_list) // 2 - asteroids_count])
        else:
            distance_list = sorted(distance_list[0:len(distance_list)])
        random_asteroid = random.randint(0, len(distance_list) - 1)
        rand = distance_list[random_asteroid][1]
        return rand


class Fighter(GlazovDrone):
    def __init__(self, unit: GlazovDrone):
        self.unit = unit
        self.used = set()
        self.stats_dict = {}
        self.stats_dict[self.unit.id] = {}
        self.condition = 'normal'
        self.target = None
        self.destination = None
        self.ready = False
        self.bornt = 0
        self.start_destination = None
        self.enemy_count = None

    def next_action(self):
        pass

    def after_born(self):
        soldier = self.unit
        soldier.move_at(soldier.start_destination)
        soldier.destination = None

    def return_after_healing(self):
        soldier = self.unit
        soldier.condition = 'normal'
        soldier.destination = soldier.start_destination
        soldier.target = None

    def fighter_actions(self):
        soldier = self.unit
        if not soldier.target:
            soldier.target = self.get_target()
        if not soldier.target.is_alive:
            soldier.target = self.get_target()
        if not soldier.destination:
            soldier.destination = self.get_place_for_attack(soldier, soldier.target)

        if hasattr(soldier.target, 'is_alive'):

            if str(soldier.coord) != str(soldier.destination):
                soldier.move_at(soldier.destination)
                return
            if soldier.distance_to(soldier.target) > soldier.gun_range and str(soldier.coord) == str(
                    soldier.destination):
                soldier.destination = self.get_place_for_attack(soldier, soldier.target)
                soldier.move_at(soldier.destination)

                return
            if soldier.distance_to(soldier.target) <= soldier.gun_range and str(soldier.coord) == str(
                    soldier.destination):
                if not self.friendly_fire(soldier.target):
                    self.fighter_attack()
                    return
                else:
                    self.destination = None
            for drones in soldier.my_team:
                if soldier.near(drones):
                    soldier.destination = None
                    return
            if not soldier.target.is_alive:
                soldier.target = None
                soldier.destination = None
                return
        else:
            soldier.target = None
            soldier.destination = None


    def fighter_attack(self):
        soldier = self.unit
        if soldier.distance_to(soldier.my_mothership) > 90:
            soldier.turn_to(soldier.target)
            soldier.gun.shot(soldier.target)

    def doing_heartbeat(self):
        soldier = self.unit

        if str(soldier.start_destination) == str(soldier.coord) and not soldier.ready:
            soldier.destination = None
            soldier.target = None
            soldier.ready = True
        if soldier.condition == 'normal' and soldier.ready:
            self.fighter_actions()

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
        vec_gunshot = norm_vec * min(self.unit.gun_range, int(dist))
        purpose = Point(target.coord.x + vec_gunshot.x, target.coord.y + vec_gunshot.y)
        angles = [0, 60, -60, 30, -30, 15, -15, 45, -45]
        random.shuffle(angles)
        for ang in angles:
            place = self.get_place_near(purpose, target, ang)
            if place and self.valide_place(place):
                return place
        return None

    def get_place_near(self, point, target, angle):
        vec = Vector(point.x - target.x, point.y - target.y)
        vec.rotate(angle)
        return Point(target.x + vec.x, target.y + vec.y)

    def valide_place(self, point: Point):
        soldier = self.unit
        is_valide = 60 < point.x < (theme.FIELD_WIDTH - 60) and 60 < point.y < (theme.FIELD_HEIGHT - 60)
        for partner in soldier.my_team:
            if not partner.is_alive or partner is self.unit:
                continue
            is_valide = is_valide and (partner.distance_to(point) >= 50)
        return is_valide

    def friendly_fire(self, enemy):
        for i in range(int(self.unit.distance_to(enemy))):
            rab = math.sqrt((int(enemy.coord.x) - int(self.unit.coord.x)) ** 2 +
                            (int(enemy.coord.y) - int(self.unit.coord.y)) ** 2)

            k = i / rab
            c_x = int(self.unit.coord.x) + (int(enemy.coord.x) - int(self.unit.coord.x)) * k
            c_y = int(self.unit.coord.y) + (int(enemy.coord.y) - int(self.unit.coord.y)) * k
            drone_list_copy = self.unit.my_team.copy()
            drone_list_copy.remove(self.unit)
            drone_list_copy = [drone for drone in drone_list_copy if drone.is_alive]
            for drone in drone_list_copy:
                drone.radius = 50
                if drone.near(Point(c_x, c_y)) or self.unit.my_mothership.near(Point(c_x, c_y)):
                    return True
                else:
                    continue

        return False

    def on_stop_at_asteroid(self, asteroid):
        pass
    def on_stop_at_mothership(self, mothership):
        pass


    def get_target(self):
        soldier = self.unit
        enemies = [(drone, soldier.distance_to(drone), drone.id) for drone in self.scene.drones if
                   soldier.team != drone.team and drone.is_alive]
        bases = [(base, soldier.distance_to(base)) for base in soldier.scene.motherships if
                 base.team != soldier.team and base.is_alive]
        bases.sort(key=lambda x: x[1])
        enemies.sort(key=lambda x: x[1])

        basa = None
        enemy = None
        self.enemy_count = len(enemies)

        if self.enemy_count > 0:
            chosen_one = enemies[0]
            enemy = chosen_one[0]

        if len(bases) > 0:
            chosen_one = bases[0]
            basa = chosen_one[0]

        if self.enemy_count <= 1 and len(bases) >= 1:
            soldier.gun_range = 550
            soldier.target = basa
            if soldier.my_number == 2:
                soldier.no_enemies = True
            return soldier.target
        elif self.enemy_count > 0 and len(bases) == 0:
            if soldier.my_number == 2:
                soldier.no_enemies = True
            soldier.target = enemy
            return soldier.target
        elif self.enemy_count == 0 and len(bases) == 0:
            self.unit.no_enemies = True
            soldier.target = None
            return soldier.target

        else:
            soldier.target = enemy
            return soldier.target

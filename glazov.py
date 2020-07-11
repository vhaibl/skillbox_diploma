# -*- coding: utf-8 -*-
import random

from astrobox.core import Drone
from robogame_engine import GameObject
from robogame_engine.geometry import Point, Vector
from robogame_engine.theme import theme

theme.FIELD_WIDTH = 900
theme.FIELD_HEIGHT = 900


class GlazovDrone(Drone):
    my_team = []

    def __init__(self, **kwargs):
        theme.PLASMAGUN_COOLDOWN_TIME = 20
        super().__init__(**kwargs)
        self.used = set()
        self.stats_dict = {}
        self.stats_dict[self.id] = {}
        self.my_team.append(self)
        # self.target = None
        self.destination = None
        if self.id == 6:
            self.job = 'worker'
        else:
            self.job = 'fighter'

    def get_target(self):

        enemies = [(drone, self.distance_to(drone)) for drone in self.scene.drones if
                   self.team != drone.team and drone.is_alive and drone.team_number == 4]

        bases = [(base, self.distance_to(base)) for base in self.scene.motherships if
                 base.team != self.team and base.is_alive]
        bases.sort(key=lambda x: x[1])
        enemies.sort(key=lambda x: x[1])

        if len(enemies) > 0:
            if self.job == 'fighter':
                chosen_one = enemies[0]
                self.target = chosen_one[0]
                return self.target
        elif len(bases) > 0:
            if self.job == 'fighter':
                chosen_one = bases.pop(0)
                self.target = chosen_one[0]
                return self.target

        elif len(enemies) == 0 and len(bases) == 0:
            self.job = 'worker'

    def get_place_for_attack(self, soldier, target):

        if isinstance(target, GameObject):
            vec = Vector.from_points(target.coord, soldier.coord)
        elif isinstance(target, Point):
            vec = Vector.from_points(target, soldier.coord)
        else:
            print(target, GameObject)
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
        is_valide = 0 < point.x < theme.FIELD_WIDTH and 0 < point.y < theme.FIELD_HEIGHT
        for partner in self.my_team:
            if not partner.is_alive or partner is self:
                continue
            is_valide = is_valide and (partner.distance_to(point) >= 50)
        return is_valide

    def _get_my_asteroid(self, dist):
        not_empty_asteroids = [asteroid for asteroid in self.scene.asteroids if asteroid.payload > 1]
        not_empty_asteroids.extend([mothership for mothership in self.scene.motherships
                                    if not mothership.is_alive and not mothership.is_empty])
        not_empty_asteroids.extend([drone for drone in self.scene.drones if not drone.is_alive and not drone.is_empty])
        for asteroid in not_empty_asteroids:

            if asteroid.payload < 1:
                not_empty_asteroids.remove(asteroid)

        for asteroid in not_empty_asteroids:
            print(asteroid, asteroid.payload)

        # print(not_empty_asteroids)
        # for delete in self.used:
        #     if delete in not_empty_asteroids:
        #         not_empty_asteroids.remove(delete)

        if len(not_empty_asteroids) == 0:
            print('      len LEN return self.my_mothership')
            return self.my_mothership

        if dist == 'distance_far':
            asteroid = self.__max_distance(not_empty_asteroids)
        elif dist == 'distance_near':
            asteroid = self.__min_distance(not_empty_asteroids)
            print('asteroid NEAR')
            print(asteroid,asteroid.payload)
            not_empty_asteroids.remove(asteroid)
        elif dist == 'distance_average':
            asteroid = self.__avg_distance(not_empty_asteroids)
        elif dist == 'distance_random':
            asteroid = self.__rand_distance(not_empty_asteroids)
        else:
            asteroid = self.__rand_distance(not_empty_asteroids)

        if not hasattr(asteroid, 'payload'):
            print('      PAYLOAD return self.my_mothership')
            return self.my_mothership

        self.used.add(asteroid)
        print('return asteroid', asteroid, asteroid.payload)
        return asteroid

    def on_born(self):
        if self.job == 'worker':
            self.destination = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.destination)

        if self.job == 'fighter':
            self.get_target_and_move()

    def turn_to(self, target, speed=None):
        if not self.is_alive:
            return
        super(Drone, self).turn_to(target, speed=1000)

    def move_at(self, target, speed=None):
        if not self.is_alive:
            return
        super(Drone, self).move_at(target, speed=1000)

    def on_hearbeat(self):

        if self.job == 'fighter':
            if self.destination and self.target:
                if str(self.coord) == str(self.destination):
                    if self.target.is_alive and self.distance_to(self.target) <= 581 and self.valide_place(self.coord):
                        self.turn_to(self.target)
                        if self.valide_place(self.coord):
                            self.gun.shot(self.target)
                        else:
                            self.get_target_and_move()
                    # elif str(self.coord) != str(self.destination) or self.distance_to(self.fighter_target) >= 580:
                    #     self.get_target_and_move()

                    else:
                        self.target = None
                        self.destination = None
                        self.get_target_and_move()
                else:
                    #TODO скорее всего здесь косяк
                    if not self.target:
                        self.get_target()
                        self.get_place_for_attack(self, self.target)

                    # if not self.destination:
                    self.get_target()

                    # self.get_place_for_attack(self, self.fighter_target)
                    self.move_at(self.destination)
            else:
                # self.target = None
                self.get_target()
                # self.destination = None
                self.get_place_for_attack(self, self.target)
        # print(self.id, self.job, self.target, self.destination)


    def get_target_and_move(self):
        if self.health <= 75:
            self.destination = self.my_mothership
            self.move_at(self.destination)

        self.target = self.get_target()
        if isinstance(self.target, GameObject):
            if self.target.is_alive or self.target.payload > 0:
                self.destination = self.get_place_for_attack(self, self.target)
                self.move_at(self.destination)

    def on_wake_up(self):
        if self.health <= 75:
                self.move_at(Point(90, 90))


        else:
            if self.job == 'worker':
                print(
                    '-------------------------------------------------------------------------------------------------')
                if self.payload < 90:

                    self.destination = self._get_my_asteroid(dist='distance_near')
                    self.move_at(self.destination)
                else:
                    self.destination = self.my_mothership
                    self.move_at(self.destination)
        #     if self.job == 'fighter':
        #         # if hasattr(self.target, 'is_alive'):
        #         if not self.target.is_alive:
        #             self.fighter_target = self.get_target()
        #             destination = self.get_place_for_attack(self, self.fighter_target)
        #             self.move_at(destination)
        #         if self.distance_to(self.fighter_target) < 580:
        #             self.turn_to(self.fighter_target)
        #             self.gun.shot(self.fighter_target)
        #         else:
        #             destination = self.get_place_for_attack(self, self.fighter_target)
        #             self.move_at(destination)

    def on_stop_at_asteroid(self, asteroid):
        if self.job == 'worker':
            self.load_from(asteroid)

    def on_load_complete(self):
        if self.job == 'worker':
            # if hasattr(self.target, 'payload'):
            if self.payload < 90 and self.target.payload <= 0:
                self.target=self._get_my_asteroid(dist='distance_near')
                self.move_at(self.target)
            else:
                self.target=self._get_my_asteroid(dist='distance_near')
                self.move_at(self.target)

            # else:
            #     self.target = self._get_my_asteroid(dist='distance_near')
            #     self.move_at(self.target)
            # self.move_at(self.my_mothership)

    def on_stop_at_mothership(self, mothership):
        if self.job == 'worker' and mothership == self.my_mothership:
            self.unload_to(mothership)
        elif self.job == 'worker' and mothership != self.my_mothership:
            self.load_from(mothership)

        if self.job == 'fighter' and self.health > 90:
            self.get_target_and_move()

    def on_unload_complete(self):
        if self.job == 'worker':
            self.target = self._get_my_asteroid(dist='distance_near')
            self.move_at(self.target)

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
        for asteroid in not_empty_asteroids: distance_list.append((self.distance_to(asteroid), asteroid))
        distance_list = sorted(distance_list)
        half_length = (len(distance_list) // 2)
        avg = distance_list[half_length][1]
        return avg

    def __rand_distance(self, not_empty_asteroids):
        distance_list = []
        for asteroid in not_empty_asteroids: distance_list.append((self.distance_to(asteroid), asteroid))
        if len(distance_list) >= 6:
            distance_list = sorted(distance_list[0:len(distance_list) // 2 - 5])
        else:
            distance_list = sorted(distance_list[0:len(distance_list)])
        random_asteroid = random.randint(0, len(distance_list) - 1)
        rand = distance_list[random_asteroid][1]
        return rand



    # # def move_at(self, target, speed=None):
    # #     if not self.is_alive:
    # #         return
    # #     self.stats()
    # #     super().move_at(target, speed=speed)
    # #     if self.target == self.my_mothership and self.is_empty:
    # #         print(
    # #             f'Дрон {self.id} пролетел {self.stats_dict[self.id]["empty"]} ед. пустым, '
    # #             f'{self.stats_dict[self.id]["partial"]} ед. частично загруженным,'
    # #             f' {self.stats_dict[self.id]["full"]} ед. полностью загруженным')
    #
    # # def stats(self):
    # #     if 'empty' not in self.stats_dict[self.id]:
    # #         self.stats_dict[self.id]['empty'] = 0
    # #         self.stats_dict[self.id]['partial'] = 0
    # #         self.stats_dict[self.id]['full'] = 0
    # #     if self.is_empty:
    # #         self.stats_dict[self.id]['empty'] += int(self.distance_to(self.target))
    # #     if self.free_space > 0 and self.free_space < 100:
    # #         self.stats_dict[self.id]['partial'] += int(self.distance_to(self.target))
    # #     if self.is_full:
    # #         self.stats_dict[self.id]['full'] += int(self.distance_to(self.my_mothership))
    # #     return self.stats_dict

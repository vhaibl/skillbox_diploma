# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField
from stage_03_harvesters.driller import DrillerDrone
from stage_03_harvesters.reaper import ReaperDrone
from stage_04_soldiers.devastator import DevastatorDrone
from glazov import GlazovDrone
from vader import VaderDrone

NUMBER_OF_DRONES = 5


class DevastatorDrone2(DevastatorDrone):
    pass


class DevastatorDrone3(DevastatorDrone):
    pass


if __name__ == '__main__':
    scene = SpaceField(
        field=(1200, 900),
        speed=5,
        asteroids_count=17,
        can_fight=True,
    )

    # team_2 = [ReaperDrone() for _ in range(NUMBER_OF_DRONES)]
    # team_3 = [DrillerDrone() for _ in range(NUMBER_OF_DRONES)]
    team_4 = [DevastatorDrone() for _ in range(NUMBER_OF_DRONES)]
    team_1 = [GlazovDrone() for _ in range(NUMBER_OF_DRONES)]

    # team_5 = [DevastatorDrone2() for _ in range(NUMBER_OF_DRONES)]
    # team_6 = [DevastatorDrone3() for _ in range(NUMBER_OF_DRONES)]
    scene.go()

# Побеждать девастаторов 1x1 чаще, чем проигрывать. БЕЗ ЧИТЕРСТВА!

# Для теста против 3 команд предлагаю тестировать в такой конфигурации
# Разобраться с этой ошибкой:
# [ERROR]: GlazovDrone:8: Exception at obj(8, p(803.4,206.6) v(178.0,1.3)) event EventWakeUp handle: 'NoneType' object has no attribute 'is_alive'

# Четвертый этап: зачёт!

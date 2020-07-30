# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField
from stage_03_harvesters.driller import DrillerDrone
from stage_03_harvesters.reaper import ReaperDrone
from stage_04_soldiers.devastator import DevastatorDrone
from glazov import GlazovDrone
from vader import VaderDrone

NUMBER_OF_DRONES = 5

if __name__ == '__main__':
    scene = SpaceField(
        field=(1200, 600),
        speed=5,
        asteroids_count=27,
        can_fight=True,
    )

    team_2 = [ReaperDrone() for _ in range(NUMBER_OF_DRONES)]
    team_3 = [DrillerDrone() for _ in range(NUMBER_OF_DRONES)]
    team_1 = [GlazovDrone() for _ in range(NUMBER_OF_DRONES)]
    team_4 = [DevastatorDrone() for _ in range(NUMBER_OF_DRONES)]
    scene.go()

# TODO - Побеждать девастаторов чаще, чем проигрывать. БЕЗ ЧИТЕРСТВА!
#  Стартовая позиция может быть в любом из 4х углов
#  Поле тоже может быть любого размера
#  После разгрома противника, нужно собирать элериум
# TODO - сатистику можно вооббще убрать

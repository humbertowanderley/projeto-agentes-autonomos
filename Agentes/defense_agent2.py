import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
import time

_DARK_TEMPLAR_NUM = 4
_STALKERS_NUM = 15

class DefenseAgent(sc2.BotAI):
    async def on_step(self, iteration):

        for gateway in self.units(GATEWAY).ready:
            #Constroi os 15 stalkers
            if self.can_afford(STALKER) and gateway.noqueue and _STALKERS_NUM > 0:
                _STALKERS_NUM = _STALKERS_NUM - 1
                await self.do(gateway.train(STALKER))

            #Constroi os 4 darks_templars
            if self.can_afford(STALKER) and gateway.noqueue and _DARK_TEMPLAR_NUM > 0:
                _DARK_TEMPLAR_NUM = _DARK_TEMPLAR_NUM -1
                await self.do(gateway.train(STALKER))


            if _STALKERS_NUM < 15:
                # self.units(STALKER)
                # .take(_STALKERS_NUM, True)
                # .move(nexus.position
                #     .towards(self.game_info.map_center, 5))
                for stalker in (self.units(STALKER).idle):
                    await self.take(stalker.move(nexus.position.towards(self.game_info.map_center, 5)))

           # if _DARK_TEMPLAR_NUM < 4:
                # self.units(DARKTEMPLAR)
                # .take(_DARK_TEMPLAR_NUM, True)
                # .move(nexus.position
                #     .towards(self.game_info.map_center, 5))

def main():
    sc2.run_game(sc2.maps.get("Simple64"), [
        Bot(Race.Protoss, DefenseAgent()),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=False)

if __name__ == '__main__':
    main()

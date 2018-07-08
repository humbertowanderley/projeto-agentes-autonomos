import sc2
from sc2 import Difficulty, Race
from sc2.constants import *
from sc2.player import Bot, Computer
import time

class ConstructorAgent(sc2.BotAI):
    def __init__(self):
        return

    async def on_step(self, iteration):

        await self.distribute_workers()
        main_nexus = self.units(NEXUS).ready.first

        if self.workers.amount < 20 and main_nexus.noqueue and self.can_afford(PROBE):
            await self.do(main_nexus.train(PROBE))

        # Dá prioridade a construção de pylons
        if self.can_afford(PYLON) and self.units(PYLON).amount <= 5:
            print('Building PYLON...')
            await self.build(PYLON, near=self.units(NEXUS).random, max_distance=30)

        # Constrói assimilators nas fontes de vespenos mais próximas ao nexus principal
        for nexus in self.units(NEXUS).ready:
            print('Looking for geysers...')
            geysers = self.state.vespene_geyser.closer_than(20.0, self.units(NEXUS).random)
            for vg in geysers:
                if not self.can_afford(ASSIMILATOR):
                    break
                    
                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    print('Building assimilator...')
                    await self.do(worker.build(ASSIMILATOR, vg))

        if self.can_afford(GATEWAY) and self.units(GATEWAY).amount < 1:
            await self.build(GATEWAY, near=self.units(PYLON).random)

        if self.can_afford(CYBERNETICSCORE) and self.units(CYBERNETICSCORE).amount < 1:
            await self.build(CYBERNETICSCORE, near=self.units(PYLON).random)
        

def main():
    sc2.run_game(sc2.maps.get('Abyssal Reef LE'), [
            Bot(Race.Protoss, ConstructorAgent()),
            Computer(Race.Protoss, difficulty=Difficulty.Hard)
        ], realtime=True)

if __name__ == '__main__':
    main()
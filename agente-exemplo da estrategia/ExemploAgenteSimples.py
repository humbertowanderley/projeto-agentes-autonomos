import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration):
        
        # Açao do BotAI que distribui os workers nos minerios e gases em relacao ao nexus mais proximo
        await self.distribute_workers()
        # Metodo para construir mais workers
        await self.build_workers()
        # Metodo para construir pylons
        await self.build_pylons()
        # Metodo para construir assimilators (coletar gas)
        await self.build_assimilators()
        # Expandir a base
        await self.expand()

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending (PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            # Existe algum gás a 15m de distancia do nexus?
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                # Pega um trabalhador proximo ao gás    
                worker = self.select_build_worker(vaspene.position)
                # Se nao existir trabalhador perto desse gás
                if worker is None:
                    break
                # O gas ja tem um assimilator?
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))
    
    async def expand(self):
        # Se tem menos de 3 unidades agrupadas no meu nexus
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            # Acao do BotAI para expandir a base
            await self.expand_now()
            await self.testAcoes()

    
    async def testAcoes(self):
        for worker in self.units(PROBE):
            await self.do(worker.stop())


run_game(maps.get("AcidPlantLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Terran, Difficulty.Easy)
    ], realtime=True)
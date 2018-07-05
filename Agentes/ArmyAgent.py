import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, ZEALOT
import random

# 165 iterations per minute

class SentdeBot(sc2.BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
        self.ENEMY_ALREADY_ATACK = False
        self.DEFENSE_SUCESSFULLY = False

    async def on_step(self, iteration):
        self.iteration = iteration
        
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
        # Criar os as construcoes de soltados
        await self.offensive_force_buildings()
        # Criar soldados
        await self.build_offensive_forces()
        # Define algumas logicas de ataque e defesa
        await self.attack()


    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE) and self.units(PROBE).amount < self.MAX_WORKERS:
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

    # Por enquanto esta sendo construida 1 gateway por minuto
    async def offensive_force_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)

            # 1 gateway por minuto
            elif len(self.units(GATEWAY)) < (self.iteration / self.ITERATIONS_PER_MINUTE):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)
    
    # 2 zealots para defesa e o resto para um possivel ataque
    async def build_offensive_forces(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(ZEALOT) and self.supply_left > 0:
                await self.do(gw.train(ZEALOT))
    
    # Nao esta sendo utilizado por enquantoß
    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # Depois de levar o primeiro ataque, pega pelo menos 6 zealots disponíveis e manda pro ataque 
        if self.units(ZEALOT).idle.amount > 6 and self.ENEMY_ALREADY_ATACK:
            for s in self.units(ZEALOT).idle:
                await self.do(s.attack(self.enemy_start_locations[0]))

        elif self.units(ZEALOT).amount > 2 and not self.ENEMY_ALREADY_ATACK:
            # idle é pra pegar os que nao estao fazendo nada no tempo atual
            if len(self.known_enemy_units) > 0:
                defense_zealots = self.units(ZEALOT).take(2)
                for s in defense_zealots:
                    # Otimo metodo para defesa local
                    self.ENEMY_ALREADY_ATACK = True
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
                if self.units(ZEALOT) != 0 :
                    self.DEFENSE_SUCESSFULLY = True


run_game(maps.get("AcidPlantLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Zerg, Difficulty.Medium)
    ], realtime=False)
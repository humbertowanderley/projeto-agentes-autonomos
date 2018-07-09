import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
import time
import asyncio

data = {}
data['warpgate_started'] = False
data['proxy_built'] = False
data['proxy_destroyed'] = False
data['ataque'] = False
data['proxy1'] = 0


class Agent:
    async def on_step(self, this, interation):
        raise NotImplementedError

class ConstructorAgent(Agent):
    async def on_step(self, this, iteration):
        # Reorganiza os workers nos slots de coleta de recursos
        await this.distribute_workers()
        
        # Se existir algum pylon construído, constrói portal -> cyberneticscore -> + 2 portais próximos a um pylon random
        if this.units(PYLON).ready.exists:
            if not this.units(GATEWAY).ready.exists and not this.units(WARPGATE).ready.exists:
                if this.can_afford(GATEWAY) and not this.already_pending(GATEWAY):
                    await this.build(GATEWAY, near=this.units(PYLON).ready.random)
            elif not this.units(CYBERNETICSCORE).exists and not this.already_pending(CYBERNETICSCORE):
                if this.can_afford(CYBERNETICSCORE):
                    await this.build(CYBERNETICSCORE, near=this.units(PYLON).ready.random)
            # elif not this.units(FORGE).exists and not this.already_pending(FORGE):
            #       if this.can_afford(FORGE):
            #               await this.build(FORGE, near=this.units(PYLON).ready.random)
            elif this.can_afford(GATEWAY) and (this.units(WARPGATE).amount + this.units(GATEWAY).amount) < 5:
                await this.build(GATEWAY, near=this.units(PYLON).ready.random)
        
        # Se a pesquisa de wargate for iniciada, constrói twilightconcil -> darkshrine -> pylon de proxy
        if(data['warpgate_started'] == True):

            if not this.units(TWILIGHTCOUNCIL).ready.exists:
                if this.can_afford(TWILIGHTCOUNCIL) and not this.already_pending(TWILIGHTCOUNCIL):
                    await this.build(TWILIGHTCOUNCIL, near=this.units(PYLON).ready.random)
            elif not this.units(DARKSHRINE).ready.exists:
                if this.can_afford(DARKSHRINE) and not this.already_pending(DARKSHRINE):
                    await this.build(DARKSHRINE, near=this.units(PYLON).random)

                if this.units(DARKSHRINE).amount >= 1 and not data['proxy_built']:
                    data['proxy1'] = this.game_info.map_center.towards(
                        this.enemy_start_locations[0], random.randrange(15, 30))
                    if this.can_afford(PYLON):
                        await this.build(PYLON, near=data['proxy1'])
                        data['proxy_built'] = True
                        data['proxy_destroyed'] = False

        # Transforma todos os gateway em warpgateways assim que a tecnologia esteja disponível. enquanto não está, cria stalkers para defesa da base principal
        for gateway in this.units(GATEWAY).ready:
            abilities = await this.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and this.can_afford(AbilityId.MORPH_WARPGATE):
                if this.units(WARPGATE).amount < 2:
                    await this.do(gateway(MORPH_WARPGATE))
            if this.can_afford(STALKER) and this.units(STALKER).amount < 10 and this.units(CYBERNETICSCORE).ready and gateway.noqueue:
                await this.do(gateway.train(STALKER))
        
        # Se o cybernetic core estiver construído e ter recuros, inicia a pesquisa de warpgate
        if this.units(CYBERNETICSCORE).ready.exists and this.can_afford(RESEARCH_WARPGATE) and not data['warpgate_started']:
            ccore = this.units(CYBERNETICSCORE).ready.random
            await this.do(ccore(RESEARCH_WARPGATE))
            data['warpgate_started'] = True

class ResourceAdminAgent(Agent):
    async def on_step(self, this, iteration):
        main_nexus = this.units(NEXUS).ready.first

        # Define a construção de Assimiladores nos vespene geysers próximos a cada nexus existente
        for nexus in this.units(NEXUS).ready:
            vespene_geysers = this.state.vespene_geyser.closer_than(
                13.0, nexus)
            for vg in vespene_geysers:
                if not this.can_afford(ASSIMILATOR):
                    break

                worker = this.select_build_worker(vg.position)
                if worker is None:
                    break

                if not this.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    await this.do(worker.build(ASSIMILATOR, vg))

        # Constroi um novo pylon próximo ao nexux principal sempre que a capacidade populacional estiver a beira de atingir o limite
        if this.supply_left < 5 and not this.already_pending(PYLON):
            if this.can_afford(PYLON):
                await this.build(PYLON, near=main_nexus.position.towards(this.game_info.map_center, 7))
            return

        # Define o número máximo de workers baseado na quantidade de nexus disponíveis e um limiar de 40 workers
        if (this.workers.amount < this.units(NEXUS).amount*20 and this.workers.amount < 40) and main_nexus.noqueue and this.supply_left > 0:
            if this.can_afford(PROBE):
                await this.do(main_nexus.train(PROBE))
            return

class DefenseAgent(Agent):

    async def on_step(self, this, iteration):
        # Defesa
        if this.known_enemy_units.amount > 0 and not data['ataque']:
            for stalker in this.units(STALKER).idle:
                await this.do(stalker.attack(this.known_enemy_units[0]))
        elif not data['ataque']:
            for stalker in this.units(STALKER).idle:
                await this.do(stalker.move(this.units(NEXUS).first))
        else:
            for templar in this.units(DARKTEMPLAR).ready:
                await this.do(templar.attack(this.enemy_start_locations[0]))
            for stalker in this.units(STALKER).ready:
                await this.do(stalker.attack(this.enemy_start_locations[0]))

class MilitaryAgent(Agent):

    async def on_step(self, this, iteration):
        # Comecar a treinar os soldados na base da gente
        if data['proxy_destroyed']:

            for gateway in this.units(GATEWAY).ready:
                if this.can_afford(DARKTEMPLAR) and this.units(DARKTEMPLAR).amount < 10 and this.units(CYBERNETICSCORE).ready and gateway.noqueue:
                    await this.do(gateway.train(DARKTEMPLAR))

            for gateway in this.units(GATEWAY).ready:
                if this.can_afford(STALKER) and this.units(STALKER).amount < 10 and this.units(CYBERNETICSCORE).ready and gateway.noqueue:
                    await this.do(gateway.train(STALKER))

            for warpgate in this.units(WARPGATE).ready:
                abilities = await this.get_available_abilities(warpgate)
                if AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                    if this.can_afford(DARKTEMPLAR):
                        placement = await this.find_placement(AbilityId.WARPGATETRAIN_STALKER, this.units(PYLON).random.position.random_on_distance(5), placement_step=5)
                        if placement is not None:
                            if this.can_afford(DARKTEMPLAR) and this.units(DARKTEMPLAR).amount < 10 and warpgate.noqueue:
                                await this.do(warpgate.warp_in(DARKTEMPLAR, placement))
                                data['ataque'] = True

            if this.units(DARKTEMPLAR).amount > 2:
                for templar in this.units(DARKTEMPLAR).ready:
                    await this.do(templar.attack(this.enemy_start_locations[0]))
                for stalker in this.units(STALKER).ready:
                    await this.do(stalker.attack(this.enemy_start_locations[0]))
             

class StrategyAgent(Agent):

    async def on_step(self, this, iteration):
        # Reorganiza os workers nos slots de coleta de recursos
        await this.distribute_workers()

        # Se não existe nenhum nexus, faz todos os workers atacarem a base inimiga
        if not this.units(NEXUS).ready.exists:
            for worker in this.workers:
                await this.do(worker.attack(this.enemy_start_locations[0]))
            return
        else:
            # define o nexus principal
            main_nexus = this.units(NEXUS).ready.first
            # Faz expansão apartir de algum tempo e se o número total de nexus for menor que 2
            if(iteration > 400 and this.units(NEXUS).amount < 2 and this.can_afford(NEXUS)):
                await this.expand_now()

        # Se o pylon de proxy está construído, transdobra darktemplar para eles assim que a unidade estiver disponível
        if data['proxy_built']:
            for warpgate in this.units(WARPGATE).ready:

                abilities = await this.get_available_abilities(warpgate)
                if AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                    # Define local de transdobra próximo ao pylon de proxy
                    if this.can_afford(DARKTEMPLAR):
                        placement = await this.find_placement(AbilityId.WARPGATETRAIN_STALKER, data['proxy1'].random_on_distance(5), placement_step=5)
                        # Se o pylon de proxy for destruído, é um problema.
                        if placement is not None:
                            await this.do(warpgate.warp_in(DARKTEMPLAR, placement))
                            data['ataque'] = True
                        else:
                            data['proxy_built'] = False
                            data['proxy_destroyed'] = True

            # Sempre que ter um templar de bobeira, manda ele atacar a base inimiga
            if this.units(DARKTEMPLAR).amount > 2:
                for templar in this.units(DARKTEMPLAR).ready:
                    await this.do(templar.attack(this.enemy_start_locations[0]))
                for stalker in this.units(STALKER).ready:
                    await this.do(stalker.attack(this.enemy_start_locations[0]))


class MainAgent(sc2.BotAI):
    def __init__(self):
        self.agents = []
    
    def on_start(self):
        self.agents.append(StrategyAgent())
        self.agents.append(MilitaryAgent())
        self.agents.append(DefenseAgent())
        self.agents.append(ResourceAdminAgent())
        self.agents.append(ConstructorAgent())

    async def on_step(self, iteration):
        loop = asyncio.get_event_loop()
        tasks = []
        for agent in self.agents:
            tasks.append(loop.create_task(agent.on_step(self, iteration)))
        done, pending = await asyncio.wait(tasks, timeout=2.0)
        for task in pending:
            task.cancel()

def main():
    sc2.run_game(sc2.maps.get("PaladinoTerminalLE"), [
        Bot(Race.Protoss, MainAgent()),
        Computer(Race.Protoss, Difficulty.Hard)
    ], realtime=False)


if __name__ == '__main__':
    main()

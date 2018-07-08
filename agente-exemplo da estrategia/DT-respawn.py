import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
import time

class MyBot(sc2.BotAI):
        def __init__(self):
                self.warpgate_started = False
                self.proxy_built = False
                self.proxy_destroyed = False
                self.ataque = False
                self.proxy1 = 0
                
        async def on_step(self, iteration):
                
                #Reorganiza os workers nos slots de coleta de recursos
                await self.distribute_workers()

                #Se não existe nenhum nexus, faz todos os workers atacarem a base inimiga
                if not self.units(NEXUS).ready.exists:
                        for worker in self.workers:
                                await self.do(worker.attack(self.enemy_start_locations[0]))
                        return
                else:
                        #define o nexus principal
                        main_nexus = self.units(NEXUS).ready.first
                        #Faz expansão apartir de algum tempo e se o número total de nexus for menor que 2
                        if(iteration > 400 and self.units(NEXUS).amount < 2 and self.can_afford(NEXUS)):
                                await self.expand_now()
                
                #Constroi um novo pylon próximo ao nexux principal sempre que a capacidade populacional estiver a beira de atingir o limite
                if self.supply_left < 5 and not self.already_pending(PYLON):
                        if self.can_afford(PYLON):
                                await self.build(PYLON, near=main_nexus.position.towards(self.game_info.map_center, 7))
                        return

                #Define o número máximo de workers baseado na quantidade de nexus disponíveis e um limiar de 40 workers
                if (self.workers.amount < self.units(NEXUS).amount*20 and self.workers.amount < 40) and main_nexus.noqueue and self.supply_left > 0:
                        if self.can_afford(PROBE):
                                await self.do(main_nexus.train(PROBE))
                        return

                #Define a construção de Assimiladores nos vespene geysers próximos a cada nexus existente
                for nexus in self.units(NEXUS).ready:
                        vespene_geysers = self.state.vespene_geyser.closer_than(13.0, nexus)
                        for vg in vespene_geysers:
                                if not self.can_afford(ASSIMILATOR):
                                        break

                                worker = self.select_build_worker(vg.position)
                                if worker is None:
                                        break

                                if not self.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                                        await self.do(worker.build(ASSIMILATOR, vg))

                #Se existir algum pylon construído, constrói portal -> cyberneticscore -> + 2 portais próximos a um pylon random
                if self.units(PYLON).ready.exists:
                        if  not self.units(GATEWAY).ready.exists and not self.units(WARPGATE).ready.exists:
                                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                                        await self.build(GATEWAY, near=self.units(PYLON).ready.random)
                        elif not self.units(CYBERNETICSCORE).exists and not self.already_pending(CYBERNETICSCORE):
                                if self.can_afford(CYBERNETICSCORE):
                                        await self.build(CYBERNETICSCORE, near=self.units(PYLON).ready.random)
                        #elif not self.units(FORGE).exists and not self.already_pending(FORGE):
                        #       if self.can_afford(FORGE):
                        #               await self.build(FORGE, near=self.units(PYLON).ready.random)
                        elif self.can_afford(GATEWAY) and (self.units(WARPGATE).amount + self.units(GATEWAY).amount) < 5:
                                await self.build(GATEWAY, near=self.units(PYLON).ready.random)

                #Se o cybernetic core estiver construído e ter recuros, inicia a pesquisa de warpgate
                if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(RESEARCH_WARPGATE) and not self.warpgate_started:
                        ccore = self.units(CYBERNETICSCORE).ready.random
                        await self.do(ccore(RESEARCH_WARPGATE))
                        self.warpgate_started = True

                #if self.units(FORGE).exists:
                    

                #Se a pesquisa de wargate for iniciada, constrói twilightconcil -> darkshrine -> pylon de proxy 
                if(self.warpgate_started == True):

                        if  not self.units(TWILIGHTCOUNCIL).ready.exists:
                                if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                                        await self.build(TWILIGHTCOUNCIL, near=self.units(PYLON).ready.random)
                        elif  not self.units(DARKSHRINE).ready.exists:
                                if self.can_afford(DARKSHRINE) and not self.already_pending(DARKSHRINE):
                                        await self.build(DARKSHRINE, near=self.units(PYLON).random)
                                        
                                if self.units(DARKSHRINE).amount >= 1 and not self.proxy_built:
                                        self.proxy1 = self.game_info.map_center.towards(self.enemy_start_locations[0], random.randrange(15, 30))
                                        if self.can_afford(PYLON):
                                                await self.build(PYLON, near=self.proxy1)
                                                self.proxy_built = True
                                                self.proxy_destroyed = False

                #Transforma todos os gateway em warpgateways assim que a tecnologia esteja disponível. enquanto não está, cria stalkers para defesa da base principal
                for gateway in self.units(GATEWAY).ready:
                        abilities = await self.get_available_abilities(gateway)
                        if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                                if self.units(WARPGATE).amount < 2:
                                        await self.do(gateway(MORPH_WARPGATE))
                        if self.can_afford(STALKER) and self.units(STALKER).amount < 10 and self.units(CYBERNETICSCORE).ready and gateway.noqueue:
                                await self.do(gateway.train(STALKER))

                #Se o pylon de proxy está construído, transdobra darktemplar para eles assim que a unidade estiver disponível
                if self.proxy_built:
                        for warpgate in self.units(WARPGATE).ready:
                                
                                abilities = await self.get_available_abilities(warpgate)
                                if AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                                        #Define local de transdobra próximo ao pylon de proxy
                                    if self.can_afford(DARKTEMPLAR):
                                        placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, self.proxy1.random_on_distance(5), placement_step=5)
                                        #Se o pylon de proxy for destruído, é um problema.
                                        if placement is not None:
                                                await self.do(warpgate.warp_in(DARKTEMPLAR, placement))
                                                self.ataque = True
                                        else:
                                            self.proxy_built = False
                                            self.proxy_destroyed = True
                                        
                        #Sempre que ter um templar de bobeira, manda ele atacar a base inimiga
                        if self.units(DARKTEMPLAR).amount > 2:
                                for templar in self.units(DARKTEMPLAR).ready:
                                        await self.do(templar.attack(self.enemy_start_locations[0]))
                                for stalker in self.units(STALKER).ready:
                                        await self.do(stalker.attack(self.enemy_start_locations[0]))

                # Comecar a treinar os soldados na base da gente
                if self.proxy_destroyed:

                        for gateway in self.units(GATEWAY).ready:
                                if self.can_afford(DARKTEMPLAR) and self.units(DARKTEMPLAR).amount < 10 and self.units(CYBERNETICSCORE).ready and gateway.noqueue:
                                        await self.do(gateway.train(DARKTEMPLAR))

                        for gateway in self.units(GATEWAY).ready:
                                if self.can_afford(STALKER) and self.units(STALKER).amount < 10 and self.units(CYBERNETICSCORE).ready and gateway.noqueue:
                                        await self.do(gateway.train(STALKER))

                                                
                        for warpgate in self.units(WARPGATE).ready:
                                abilities = await self.get_available_abilities(warpgate)
                                if AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities:
                                        if self.can_afford(DARKTEMPLAR):
                                                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, self.units(PYLON).random.position.random_on_distance(5), placement_step=5)
                                                if placement is not None:
                                                        if self.can_afford(DARKTEMPLAR) and self.units(DARKTEMPLAR).amount < 10 and warpgate.noqueue:
                                                                await self.do(warpgate.warp_in(DARKTEMPLAR, placement))
                                                                self.ataque = True

                        if self.units(DARKTEMPLAR).amount > 2:
                                for templar in self.units(DARKTEMPLAR).ready:
                                        await self.do(templar.attack(self.enemy_start_locations[0]))
                                for stalker in self.units(STALKER).ready:
                                        await self.do(stalker.attack(self.enemy_start_locations[0]))

                # Defesa
                if self.known_enemy_units.amount > 0 and not self.ataque:
                    for stalker in self.units(STALKER).idle:
                        await self.do(stalker.attack(self.known_enemy_units[0]))
                elif not self.ataque:
                    for stalker in self.units(STALKER).idle:
                        await self.do(stalker.move(self.units(NEXUS).first))
                else:
                        for templar in self.units(DARKTEMPLAR).ready:
                                await self.do(templar.attack(self.enemy_start_locations[0]))
                        for stalker in self.units(STALKER).ready:
                                await self.do(stalker.attack(self.enemy_start_locations[0]))

                                
def main():
        sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
                Bot(Race.Protoss, MyBot()),
                Computer(Race.Protoss, Difficulty.Hard)
        ], realtime=False)

if __name__ == '__main__':
        main()

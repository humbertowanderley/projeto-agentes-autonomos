import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
import time
		
#Representação da tabela de memória compartilhada
memoria = [0, 0, 0, 0, 1, 0, 0, 0, 0, []]
		
class ResourceAgent(sc2.BotAI):
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
			if(iteration > 500 and memoria[4] < 2 and self.can_afford(NEXUS)):
				await self.expand_now()
				memoria[4] = memoria[4] + 1
				s = 'A quantidade de nexus é ' + repr(memoria[4])
				print(s)
		
		#Constroi um novo pylon próximo ao nexux principal sempre que a capacidade populacional estiver a beira de atingir o limite
		if self.supply_left < 5 and not self.already_pending(PYLON):
			if self.can_afford(PYLON):
				await self.build(PYLON, near=main_nexus.position.towards(self.game_info.map_center, 3))
			return

		#Define o número máximo de workers baseado na quantidade de nexus disponíveis e um limiar de 40 workers
		if (self.workers.amount < self.units(NEXUS).amount*20 and self.workers.amount < 40) and main_nexus.noqueue and self.supply_left > 0:
			if self.can_afford(PROBE):
				await self.do(main_nexus.train(PROBE))
			return

		#Define a construção de Assimiladores nos vespene geysers próximos a cada nexus existente
		for nexus in self.units(NEXUS).ready:
			vespene_geysers = self.state.vespene_geyser.closer_than(20.0, nexus)
			for vg in vespene_geysers:
				if not self.can_afford(ASSIMILATOR):
					break

				worker = self.select_build_worker(vg.position)
				if worker is None:
					break

				if not self.units(ASSIMILATOR).closer_than(1.0, vg).exists:
					await self.do(worker.build(ASSIMILATOR, vg))

def main():
	sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
		Bot(Race.Protoss, ResourceAgent()),
		Computer(Race.Protoss, Difficulty.Easy)
	], realtime=False)

if __name__ == '__main__':
	main()
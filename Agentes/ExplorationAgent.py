import random

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from math import sqrt

# from sc2.constants import *
import time

class ExplorationAgent(sc2.BotAI):
    
    def __init__(self):
        
        self.pylonList = []
        self.enemy_location = None
        self.explorer = None

    async def on_step(self, iteration):
        
        # Açao do BotAI que distribui os workers nos minerios e gases em relacao ao nexus mais proximo
        await self.distribute_workers()
        # Metodo para construir mais workers
        await self.build_workers()
       
       
        # Verifica onde o inimigo nasceu
        await self.find_enemy_start_locations()
        
        if self.enemy_location is None:
            self.enemy_location = await self.enemy_start_location()
        

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))


    async def build_pylon_close_enemy(self, location = None):
        '''
			Constroi um pylon em um local proximo ao local do inimigo
		'''
        if location is None: 
            location = self.enemy_start_locations[0]

        self.proxy1 = self.game_info.map_center.towards(location, random.randrange(15, 30))
        if self.can_afford(PYLON):
            await self.build(PYLON, near=self.proxy1)
            self.pylonList.append(self.proxy1)
            print("position: {0}".format(self.proxy1))


    async def find_enemy_start_locations(self):
        '''
			Procura onde é local de nascimento do inimigo
		'''
        if self.explorer is None:
		    #seleciona um trabalhador
            self.explorer = self.units(PROBE).first
        
		#para cada possivel localizacao da base inimiga manda o trabalhador para lá
        for location in self.enemy_start_locations:
            await self.do(self.explorer.move(location))


    async def select_random_enemy_structure(self):
        '''
			Seleciona uma estrutura do inimigo randomicamente, 
            caso o explorador ainda não tenha encontrado o local 
            do inimigo retorna None
		'''
        if self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures)
        
        return None
    

    async def enemy_start_location(self):
        '''
			Com base na localização de uma estrutura randomica
            do inimigo retorna a posição do inimigo, caso o 
            explorador ainda não tenha encontrado o local do 
            inimigo retorna None
		'''
        structure = await self.select_random_enemy_structure()
        
        if structure is None:
            return None
        else:
            position = structure.position
            index = 0
            min = float("inf")
        
            for i in range(len(self.enemy_start_locations)):
                location = self.enemy_start_locations[i]
                dist = sqrt( (location.x - position.x)**2 + (location.y - position.y)**2 )
                if dist < min :
                    min = dist
                    index = i
            
            return self.enemy_start_locations[index]


def main():
    sc2.run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Protoss, ExplorationAgent()),
        Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
	main()

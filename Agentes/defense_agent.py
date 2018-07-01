
from pysc2.agents import base_agent
from pysc2.lib import actions

import time

# Funcoes de Defesa
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_TRAIN_DARK_TEMPLAR = actions.FUNCTIONS.Train_DarkTemplar_quick.id #cria o soldado dark
_TRAIN_STALKER = actions.FUNCTIONS.Train_Stalker_quick.id #cria o soldado stalker
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id # <= Cria o ponto de encontro ao criar as unidades. Nao sei como podemos usar ja que n temos mapa certo definido
_SELECT_ARMY = actions.FUNCTIONS.select_army.id # <= Selecionar todas as minhas tropas (acho que n posso usar porque temos tropas divididas)
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id # <= Usar quando precisar me defender

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index # <=
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index  # <= Util para selecionar unidades

# Unidades ID Protoss
_PROTOSS_STALKER = 74
_PROTOSS_DARKTEMPLAR = 76


# Parametros
_DARK_TEMPLAR_MAX = 4
_STALKERS_MAX = 15
_NOT_QUEUED = [0]
_QUEUED = [1]

# Espero que tenha na memória compartilhada
gateway_built = False
warp_gate_built = False
max_capacity = False

class DefenseAgent(base_agent.BaseAgent):
	stalkers_selected = False
	dark_templars_selected = False

	#Seleciona os Stalkers
	def SelectStalkers(self, obs):
		super(DefenseAgent, self).step(obs)

		    unit_type = obs.observation["screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _PROTOSS_STALKER).nonzero()

            stalkers_selected = True
            stalkers = [unit_x, unit_y]


		return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, stalkers])

	#Seleciona os Dark Templars
	def SelectDarkTemplars(self, obs):
		super(DefenseAgent, self).step(obs)

		    unit_type = obs.observation["screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _PROTOSS_DARKTEMPLAR).nonzero()

            dark_templars_selected = True
            dark_templars = [unit_x, unit_y]


		return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, dark_templars])

	#Criar os Stalkers
	def TrainStalkers(self, obs):
		super(DefenseAgent, self).step(obs)

		if(not max_capacity 
			and _TRAIN_STALKER in obs.observation["available_actions"]
			and _STALKERS_MAX > 0):

			_STALKERS_MAX = _STALKERS_MAX + 1

            return actions.FunctionCall(_TRAIN_STALKER, [_QUEUED])

		return actions.FunctionCall(_NOOP, [])


	#Cria os DarkTemplairs
	def TrainDarkTemplairs(self, obs):
		super(DefenseAgent, self).step(obs)

		if(not max_capacity 
			and _TRAIN_DARK_TEMPLAR in obs.observation["available_actions"]
			and _DARK_TEMPLAR_MAX > 0):

			_DARK_TEMPLAR_MAX = _DARK_TEMPLAR_MAX + 1

            return actions.FunctionCall(_TRAIN_DARK_TEMPLAR, [_QUEUED])

		return actions.FunctionCall(_NOOP, [])

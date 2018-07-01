
from pysc2.agents import base_agent
from pysc2.lib import actions

import time

# Funcoes de Defesa
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_TRAIN_DARK_TEMPLAR = actions.FUNCTIONS.Train_DarkTemplar_quick.id
_TRAIN_STALKER = actions.FUNCTIONS.Train_Stalker_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

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

	def SelectStalkers(self, obs):
		super(DefenseAgent, self).step(obs)

		    unit_type = obs.observation["screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _PROTOSS_STALKER).nonzero()

            stalkers_selected = True
            stalkers = [unit_x, unit_y]


		return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, stalkers])


	def SelectDarkTemplars(self, obs):
		super(DefenseAgent, self).step(obs)

		    unit_type = obs.observation["screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _PROTOSS_DARKTEMPLAR).nonzero()

            dark_templars_selected = True
            dark_templars = [unit_x, unit_y]


		return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, dark_templars])

	def TrainStalkers(self, obs):
		super(DefenseAgent, self).step(obs)

		if(!max_capacity 
			and _TRAIN_STALKER in obs.observation["available_actions"]
			and _STALKERS_MAX > 0):

			_STALKERS_MAX = _STALKERS_MAX + 1

            return actions.FunctionCall(_TRAIN_STALKER, [_QUEUED])

		return actions.FunctionCall(_NOOP, [])


	def TrainDarkTemplairs(self, obs):
		super(DefenseAgent, self).step(obs)

		if(!max_capacity 
			and _TRAIN_DARK_TEMPLAR in obs.observation["available_actions"]
			and _DARK_TEMPLAR_MAX > 0):

			_DARK_TEMPLAR_MAX = _DARK_TEMPLAR_MAX + 1

            return actions.FunctionCall(_TRAIN_DARK_TEMPLAR, [_QUEUED])

		return actions.FunctionCall(_NOOP, [])

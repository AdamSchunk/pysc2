# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Define the mini game map configs. These are maps made by Deepmind."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pysc2.maps import lib


class MiniGame(lib.Map):
  directory = "mini_games"
  download = "https://github.com/deepmind/pysc2#get-the-maps"
  players = 1
  score_index = 0
  game_steps_per_episode = 0
  step_mul = 8


mini_games = [
    "BuildMarines",  # 900s
    "CollectMineralsAndGas",  # 420s
    "CollectMineralShards",  # 120s
    "DefeatRoaches",  # 120s
    "DefeatZerglingsAndBanelings",  # 120s
    "FindAndDefeatZerglings",  # 180s
    "MoveToBeacon",  # 120s
	"RandomEngagements", #60s
	"RandomEngagements_max3groups_max10units", #60s
	"ControlAreaPatrol", #120s
	"RandomEngagements_max1groups_max10units", #60s
	"rndmEng_map_1g_10u", #60s
	"testSecondSave", #60s
	"endGameAfter5SecondsonAgria", #5s
	"endGameAfter5SecondsOnCatalyst", #5s
	"endGameAfter5SecondsOnAgria_cameraSet_noMeleInit", #5s
	"Agria_d20",
	"Agria_d50",
	"Agria_d100",
	"Agria_noCam",
	"agaria_base_5sEnd",
	"agaria_base_5sEnd_noMeeleInit",
	"agaria_base_5sEnd_emptyInit",
	"agaria_base_5sEnd_defaultMeeleOptions",
]


for name in mini_games:
  globals()[name] = type(name, (MiniGame,), dict(filename=name))

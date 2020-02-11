#!/usr/bin/env python3.6

# Put underscore to avoid showing as public imports
import rospy as _rospy
import os as _os
from abm_grant_interaction.data_structures import StateDb as _StateDb
from abm_grant_interaction.data_structures import ParameterDb as _ParameterDb
from interaction_engine.text_populator import TextPopulator as _TextPopulator
from interaction_engine.text_populator import DatabasePopulator as _DatabasePopulator
from interaction_engine.text_populator import VarietyPopulator as _VarietyPopulator


_resources_directory = _rospy.get_param(
    'abm/resources/path',
    default="/root/ws/catkin_ws/src/abm_interaction/resources",
)
_main_variation_file = 'variation.csv'
_big_5_variation_file = 'big_5_questions.csv'


_state_directory = _rospy.get_param(
    'abm/state/path',
    default="/root/state",
)
_state_db_file = 'state_db.pkl'
_param_db_file = 'param_db.pkl'


# Create state and param databases
_os.makedirs(_state_directory, exist_ok=True)

_state_db_path = _os.path.join(_state_directory, _state_db_file)
state_db = _StateDb(_state_db_path)

_param_db_path = _os.path.join(_state_directory, _param_db_file)
param_db = _ParameterDb(_param_db_path)

# Create a 'TextPopulator'
_main_variation_path = _os.path.join(_resources_directory, _main_variation_file)
_big_5_variation_path = _os.path.join(_resources_directory, _big_5_variation_file)
assert _os.path.exists(_main_variation_path)
assert _os.path.exists(_big_5_variation_path)

_variety_populator = _VarietyPopulator(
    files=[
        _main_variation_path,
        _big_5_variation_path
    ],
)
_database_populator = _DatabasePopulator(state_db)
text_populator = _TextPopulator(_variety_populator, _database_populator)

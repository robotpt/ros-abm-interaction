#!/usr/bin/python
# Put underscore to avoid showing as public imports
import os as _os
import yaml as _yaml
from abm_grant_interaction.data_structures import StateDb as _StateDb
from abm_grant_interaction.data_structures import ParameterDb as _ParameterDb
from interaction_engine.text_populator import TextPopulator as _TextPopulator
from interaction_engine.text_populator import DatabasePopulator as _DatabasePopulator
from interaction_engine.text_populator import VarietyPopulator as _VarietyPopulator
from robotpt_common_utils import user_input


# Should be in 'resources' directory
_main_variation_file = 'variation.csv'
_big_5_variation_file = 'big_5_questions.csv'
_fitbit_secrets_file = 'fitbit_secrets.yaml'


# Created in 'temp' directory
_state_db_file = 'state_db.pkl'
_param_db_file = 'param_db.pkl'


# In top directory
_config_file = 'config.yaml'


# Get path relative to this file
_src_directory_path = _os.path.dirname(_os.path.realpath(__file__))
_relative_path_to_resources_directory = _os.path.join('..', 'resources')
_resources_directory = _os.path.join(_src_directory_path, _relative_path_to_resources_directory)
assert _os.path.exists(_resources_directory)


# Get path to config file
_path_to_top_directory = _os.path.join(_src_directory_path, '..')
_config_file_path = _os.path.join(_path_to_top_directory, _config_file)

# Setup variables from config
with open(_config_file_path, 'r') as f:
    _data = _yaml.load(f, Loader=_yaml.FullLoader)
IS_DEBUG = _data['debug']


# Get path to Fitbit secret client info
_fitbit_secrets_path = _os.path.join(_resources_directory, _fitbit_secrets_file)
if not _os.path.exists(_fitbit_secrets_path):
    print("Please pair with your fitbit account")

    is_have_account = user_input.is_yes(input("Do you have an app? (yes or no)\n>>> "))
    if not is_have_account:
        print(
            "Here is how to create a fitbit app to give this program access to your fitbit data\n" 
            "\t1. Go to https://dev.fitbit.com/apps/new\n" 
            "\t2. Fill in the form information\n" 
            "\t\t * For websites you can use https://www.google.com)\n" 
            "\t\t * For 'OAuth 2.0 Application Type' select 'Personal'\n" 
            "\t\t * For 'Callback URL' put 'http://127.0.0.1:8080/'\n" 
            "\t\t * And request 'Read Only' data access\n" 
            "\t3. Navigate to see the app details for the client ID and client secret"
        )
        input("Hit 'Enter' to continue")
    client_id = input("Please enter your app's client id\n>>> ")
    client_secret = input("Please enter your app's client secret\n>>> ")
    with open(_fitbit_secrets_path, 'w') as f:
        _yaml.dump({'client_id': client_id, 'client_secret': client_secret}, f)
    print(f"File '{_fitbit_secrets_path}' created - please modify that file if needed")


# Create state and param databases
_relative_path_to_temp_directory = _os.path.join('..', 'temp')
_temp_directory = _os.path.join(_src_directory_path, _relative_path_to_temp_directory)
_os.makedirs(_temp_directory, exist_ok=True)

_state_db_path = _os.path.join(_temp_directory, _state_db_file)
state_db = _StateDb(_state_db_path)

_param_db_path = _os.path.join(_temp_directory, _param_db_file)
param_db = _ParameterDb(_param_db_path, _fitbit_secrets_path)

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

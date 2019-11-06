from pickled_database import PickledDatabase
import datetime


def get_state_database(file='state.pkl'):

    state_db = PickledDatabase(file)

    state_db.create_key_if_not_exists(
        'user_name',
        tests=lambda x: type(x) is str
    )
    state_db.create_key_if_not_exists(
        'first_meeting',
        tests=lambda x: type(x) is datetime.datetime
    )

    return state_db
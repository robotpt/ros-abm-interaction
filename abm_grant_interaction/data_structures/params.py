from pickled_database import PickledDatabase


def get_params_database(file='params.pkl'):

    params_db = PickledDatabase(file)

    params_db.create_key_if_not_exists(
        'param1', 1
    )

    return params_db

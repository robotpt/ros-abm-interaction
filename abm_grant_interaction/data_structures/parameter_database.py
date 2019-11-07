from pickled_database import PickledDatabase


class ParameterDb(PickledDatabase):

    class Keys:
        STEPS_PER_MINUTE_FOR_ACTIVE = 'steps_per_minute_for_active'
        ACTIVE_MINS_TO_REGISTER_ACTIVITY = 'active_minutes_to_register_activity'
        CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK = \
            'consecutive_minutes_inactive_before_breaking_activity_streak'
        INACTIVE_INTERACTION_TIMEOUT_SECONDS = 'inactive_interaction_timeout_seconds'
        FITBIT_PULL_RATE_MINS = 'fitbit_pull_rate_minutes'
        MINUTES_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING = \
            'mins_before_warning_about_fitbit_not_syncing'

    def __init__(self, database_path='parameters.pkl'):
        super().__init__(database_path=database_path)
        self._build()

    def set(self, key, value):
        raise PermissionError("Parameters are read only")

    def _build(self):

        self.create_key_if_not_exists(
            ParameterDb.Keys.STEPS_PER_MINUTE_FOR_ACTIVE,
            1
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.ACTIVE_MINS_TO_REGISTER_ACTIVITY,
            10
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK,
            2
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.INACTIVE_INTERACTION_TIMEOUT_SECONDS,
            45
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.FITBIT_PULL_RATE_MINS,
            2
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.MINUTES_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING,
            15
        )

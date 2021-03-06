from pickled_database import PickledDatabase
from robotpt_common_utils import math_tools
import yaml


class ParameterDb(PickledDatabase):

    class Keys:

        MAX_NUM_QUESTIONS = 'max_number_of_questions'
        INACTIVE_INTERACTION_TIMEOUT_SECONDS = 'inactive_interaction_timeout_seconds'
        NUM_OPTIONS_TO_DISPLAY = 'number_of_options_to_display'

        STEPS_PER_MINUTE_FOR_ACTIVE = 'steps_per_minute_for_active'
        ACTIVE_MINS_TO_REGISTER_ACTIVITY = 'active_minutes_to_register_activity'
        CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK = \
            'consecutive_minutes_inactive_before_breaking_activity_streak'

        WEEKS_WITH_ROBOT = 'weeks_with_robot'

        FINAL_STEPS_GOAL = 'final_steps_goal'
        MIN_WEEKLY_STEPS_GOAL = 'min_weekly_steps_goal'
        MINS_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING = \
            'minutess_before_warning_about_fitbit_not_syncing'

        FITBIT_PULL_RATE_MINS = 'fitbit_pull_rate_minutes'

        MINS_BEFORE_ALLOW_CHECKIN = 'minutes_before_allow_checkin'
        MINS_AFTER_ALLOW_CHECKIN = 'minutes_after_allow_checkin'

    def __init__(self, database_path='parameters.pkl'):
        super().__init__(database_path=database_path)
        self._build()

    def set(self, key, value):
        raise PermissionError("Parameters are read only")

    def _build(self):

        check_non_negative_int = [
            lambda x: math_tools.is_int(x),
            lambda x: x >= 0,
        ]

        self.create_key_if_not_exists(
            ParameterDb.Keys.FINAL_STEPS_GOAL,
            10000,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.MIN_WEEKLY_STEPS_GOAL,
            2000,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.WEEKS_WITH_ROBOT,
            6,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.MAX_NUM_QUESTIONS,
            3,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.NUM_OPTIONS_TO_DISPLAY,
            3,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.STEPS_PER_MINUTE_FOR_ACTIVE,
            60,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.ACTIVE_MINS_TO_REGISTER_ACTIVITY,
            10,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK,
            2,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.INACTIVE_INTERACTION_TIMEOUT_SECONDS,
            360,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.MINS_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING,
            15,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.FITBIT_PULL_RATE_MINS,
            2,
            tests=check_non_negative_int
        )
        self.create_key_if_not_exists(
            ParameterDb.Keys.MINS_BEFORE_ALLOW_CHECKIN,
            60,
            tests=check_non_negative_int
        )

        self.create_key_if_not_exists(
            ParameterDb.Keys.MINS_AFTER_ALLOW_CHECKIN,
            60,
            tests=check_non_negative_int
        )

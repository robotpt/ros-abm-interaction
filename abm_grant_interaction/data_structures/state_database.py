from abm_grant_interaction.bkt.bkt import Bkt

from pickled_database import PickledDatabase
from robotpt_common_utils import math_tools
import datetime


class StateDb(PickledDatabase):

    class Keys:
        USER_NAME = 'user_name'
        FIRST_MEETING = 'first_meeting'
        AM_CHECKIN_TIME = 'am_checkin_time'
        PM_CHECKIN_TIME = 'pm_checkin_time'
        WALK_TIME = 'walk_time'
        WALK_PLACES = 'walk_places'
        BKT = 'bkt'
        STEPS_ACTUAL_RECORD = 'steps_actual_record'
        STEPS_GOAL_RECORD = 'steps_goal_record'
        IS_MET_GOAL_RECORD = 'is_met_goal_record'
        SUGGESTED_STEPS_TODAY = 'suggested_steps_today'
        STEPS_TODAY = 'steps_today'
        STEPS_THIS_WEEK = 'steps_this_week'
        STEPS_LAST_WEEK = 'steps_last_week'
        LAST_FITBIT_SYNC = 'last_fitbit_sync'
        DAY_OFF = 'day_off'
        PSYCH_QUESTION_INDEX = 'psych_question_index'
        PSYCH_QUESTION_ANSWERS = 'psych_question_ANSWERS'

    def __init__(
            self,
            database_path='state.pkl',
    ):
        super().__init__(database_path=database_path)
        self._build()

    def _build(self):

        self.create_key_if_not_exists(
            StateDb.Keys.USER_NAME,
            tests=[
                lambda x: type(x) is str,
                lambda x: len(x) > 1,
            ],
        )
        self.create_key_if_not_exists(
            StateDb.Keys.FIRST_MEETING,
            tests=lambda x: type(x) is datetime.datetime
        )
        self.create_key_if_not_exists(
            StateDb.Keys.AM_CHECKIN_TIME,
            tests=lambda x: type(x) is datetime.time
        )
        self.create_key_if_not_exists(
            StateDb.Keys.PM_CHECKIN_TIME,
            tests=lambda x: type(x) is datetime.time
        )
        self.create_key_if_not_exists(
            StateDb.Keys.WALK_TIME,
            tests=lambda x: type(x) is datetime.time
        )
        self.create_key_if_not_exists(
            StateDb.Keys.WALK_PLACES,
            ['park', 'neighborhood', 'inside']
        )
        self.create_key_if_not_exists(
            StateDb.Keys.BKT,
            tests=lambda x: type(x) is Bkt
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_ACTUAL_RECORD,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_GOAL_RECORD,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.IS_MET_GOAL_RECORD,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.SUGGESTED_STEPS_TODAY,
            tests=lambda x: math_tools.is_int(x),
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_TODAY,
            tests=lambda x: math_tools.is_int(x),
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_THIS_WEEK,
            tests=lambda x: math_tools.is_int(x),
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_LAST_WEEK,
            tests=lambda x: math_tools.is_int(x),
        )
        self.create_key_if_not_exists(
            StateDb.Keys.LAST_FITBIT_SYNC,
            tests=lambda x: type(x) is datetime.datetime
        )
        self.create_key_if_not_exists(
            StateDb.Keys.DAY_OFF,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.PSYCH_QUESTION_INDEX,
            0,
            tests=[
                lambda x: math_tools.is_int(x),
            ]
        )
        self.create_key_if_not_exists(
            StateDb.Keys.PSYCH_QUESTION_ANSWERS,
        )

from abm_grant_interaction.bkt.bkt import Bkt

from pickled_database import PickledDatabase
from robotpt_common_utils import math_tools
import datetime


class StateDb(PickledDatabase):

    class Keys:

        USER_NAME = 'user_name'

        FIRST_MEETING = 'first_meeting'
        IS_DONE_AM_CHECKIN_TODAY = 'is_done_am_checkin_today'
        IS_DONE_PM_CHECKIN_TODAY = 'is_done_pm_checkin_today'
        IS_MISSED_PM_YESTERDAY = 'is_missed_pm_yesterday'
        CURRENT_DATETIME = 'current_datetime'

        AM_CHECKIN_TIME = 'am_checkin_time'
        PM_CHECKIN_TIME = 'pm_checkin_time'
        DAY_OFF = 'day_off'

        WALK_TIME = 'walk_time'
        WALK_PLACES = 'walk_places'
        FAIL_WHY = 'why_failed'
        HOW_BUSY = 'how_busy'
        HOW_REMEMBER = 'how_remember'
        HOW_MOTIVATE = 'how_motivate'

        BKT_pL = 'bkt_pL'
        BKT_pT = 'bkt_pT'
        BKT_pS = 'bkt_pS'
        BKT_pG = 'bkt_pG'
        IS_MET_GOAL_RECORD = 'is_met_goal_record'

        LAST_FITBIT_SYNC = 'last_fitbit_sync'
        STEPS_GOAL = 'steps_goal'
        SUGGESTED_STEPS_TODAY = 'suggested_steps_today'
        STEPS_TODAY = 'steps_today'
        STEPS_THIS_WEEK = 'steps_this_week'
        STEPS_LAST_WEEK = 'steps_last_week'

        PSYCH_QUESTION_INDEX = 'psych_question_index'
        PSYCH_QUESTION_ANSWERS = 'psych_question_ANSWERS'

    def __init__(
            self,
            database_path='state.pkl',
    ):
        super().__init__(database_path=database_path)
        self._build()

    def reset(self):
        super().clear_database()
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
            StateDb.Keys.IS_DONE_AM_CHECKIN_TODAY,
            tests=lambda x: type(x) is bool
        )
        self.create_key_if_not_exists(
            StateDb.Keys.IS_DONE_PM_CHECKIN_TODAY,
            tests=lambda x: type(x) is bool
        )
        self.create_key_if_not_exists(
            StateDb.Keys.IS_MISSED_PM_YESTERDAY,
            tests=lambda x: type(x) is bool
        )
        self.create_key_if_not_exists(
            StateDb.Keys.CURRENT_DATETIME,
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
            StateDb.Keys.HOW_BUSY,
            [
                'Plan with my calendar',
                'Walk earlier or later in the day',
                'Walk during meetings',
            ]
        )
        self.create_key_if_not_exists(
            StateDb.Keys.FAIL_WHY,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.HOW_MOTIVATE,
            [
                'Think of the health benefits',
                'Walk with a friend',
                'Listen to music while walking',
            ]
        )
        self.create_key_if_not_exists(
            StateDb.Keys.HOW_REMEMBER,
            [
                'Walk before or after lunch',
                'Set an alarm',
                'Put it on my calendar or todo list',
            ]
        )
        self.create_key_if_not_exists(
            StateDb.Keys.BKT_pL,
            0.0,
            tests=lambda x: 0 <= x < 1,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.BKT_pT,
            0.02,
            tests=lambda x: 0 <= x <= 1,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.BKT_pS,
            0.3,
            tests=lambda x: 0 <= x <= 1,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.BKT_pG,
            0.5,
            tests=lambda x: 0 <= x <= 1,
        )
        self.create_key_if_not_exists(
            StateDb.Keys.STEPS_GOAL,
            tests=lambda x: math_tools.is_int(x),
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

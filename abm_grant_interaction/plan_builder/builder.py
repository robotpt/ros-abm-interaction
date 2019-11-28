from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.bkt.bkt import Bkt
from abm_grant_interaction.interactions import \
    AmCheckin, PmCheckin, Common, FirstMeeting, OffCheckin, Options, \
    possible_plans
from interaction_engine.planner import MessagerPlanner
from datetimerange import DateTimeRange
import datetime
import math
import random


class PlanBuilder:

    def build(self):
        planner = MessagerPlanner(possible_plans)

        if self._is_first_meeting():
            self._build_first_meeting(planner)
        else:
            self._build_greeting(planner)
            if self.is_am_checkin():
                self._build_am_checkin(planner)
            elif self.is_pm_checkin():
                self._build_pm_checkin(planner)
            else:
                self._build_off_checkin(planner)
            self._build_closing(planner)

        return planner

    def _build_first_meeting(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)

        planner.insert(
            FirstMeeting.first_meeting,
            post_hook=self._set_vars_after_first_meeting
        )

        return planner

    def _build_greeting(self, planner):
        current_hour = self._current_datetime.hour
        if current_hour < 12:
            planner.insert(Common.Messages.greeting_morning)
        elif current_hour < 18:
            planner.insert(Common.Messages.greeting_afternoon)
        else:
            planner.insert(Common.Messages.greeting_evening)
        return planner

    def _build_closing(self, planner):
        current_hour = self._current_datetime.hour
        if current_hour < 12:
            planner.insert(Common.Messages.closing_morning)
        elif current_hour < 19:
            planner.insert(Common.Messages.closing_afternoon)
        else:
            planner.insert(Common.Messages.closing_night)

        return planner

    def _set_vars_after_first_meeting(self):
        state_db.set(state_db.Keys.FIRST_MEETING, self._current_datetime)
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_REDO_SCHEDULE, True)

    def _build_am_checkin(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)

        planner.insert(Common.Messages.greeting)
        if self._is_missed_pm_yesterday:
            planner.insert(Common.Messages.missed_checkin)
        planner.insert(AmCheckin.Messages.set_goal)
        planner.insert(self._build_am_questions())

        planner.insert(
            Common.Messages.closing,
            post_hook=lambda: state_db.set(
                state_db.Keys.IS_DONE_AM_CHECKIN_TODAY,
                True
            )
        )
        return planner

    def _build_am_questions(self):
        num_ii_qs = self._get_num_ii_questions(
            self._max_ii_questions,
            self._automaticity,
        )
        ii_qs = [
                    AmCheckin.where_graph,
                    AmCheckin.Messages.when_question,
                    random.choice([
                        AmCheckin.how_busy_graph,
                        AmCheckin.how_remember_graph,
                        AmCheckin.how_motivated_graph,
                    ])
                ]
        ii_qs_to_ask = min(len(ii_qs), num_ii_qs)

        questions = list()
        questions += random.sample(
            ii_qs,
            ii_qs_to_ask,
        )
        for _ in range(self._max_ii_questions-ii_qs_to_ask):
            questions.append(AmCheckin.Messages.big_5_question)

        return questions

    def _get_num_ii_questions(self, max_qs, automaticity):
        if not (0 <= automaticity <= 1):
            raise ValueError("Automaticity should be between 0-1")
        return max(math.ceil((max_qs+1)*(1-automaticity))-1, 0)

    def _build_pm_checkin(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)

        if not self._is_done_am_checkin_today:
            planner.insert(Common.Messages.missed_checkin)
        else:
            if self._is_met_steps_goal_today():
                planner.insert(
                    PmCheckin.success_graph,
                    post_hook=lambda: self._mark_pm_checkin_complete(True)
                )
            else:
                planner.insert(
                    PmCheckin.fail_graph,
                    post_hook=lambda: self._mark_pm_checkin_complete(False)
                )

        return planner

    def _mark_pm_checkin_complete(self, result):
        self._bkt_update_pL(result)
        state_db.set(
            state_db.Keys.IS_DONE_PM_CHECKIN_TODAY,
            True,
        )

    def _build_off_checkin(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)

        if self._is_time_for_status_update():
            planner.insert(OffCheckin.Messages.give_status)
        planner.insert(
            Options.options,
            post_hook=lambda: state_db.set(
                state_db.Keys.IS_REDO_SCHEDULE, True
            )
        )

        return planner

    def _is_time_for_status_update(self, current_datetime=None):
        if current_datetime is None:
            current_datetime = self._current_datetime
        return (
                self._is_done_am_checkin_today
                and not self._is_done_pm_checkin_today
                and current_datetime < self._pm_checkin_datetime
        )

    def _is_first_meeting(self):
        return not state_db.is_set(state_db.Keys.FIRST_MEETING)

    def is_am_checkin(self):
        is_time_window = _is_during_checkin_time_window(
            self._current_datetime,
            self._am_checkin_datetime,
            self._mins_before_checkin_allowed,
            self._mins_after_checkin_allowed,
        )
        return is_time_window and not self._is_done_am_checkin_today

    def is_pm_checkin(self):
        return (
                self._current_datetime >= self._pm_checkin_datetime -
                datetime.timedelta(minutes=self._mins_before_checkin_allowed) and
                not self._is_done_pm_checkin_today
        )

    def _is_met_steps_goal_today(self):
        return self._steps_today >= self._goal_today

    def _bkt_update_pL(self, observations):
        self._bkt = self._bkt.update(observations)

    def _bkt_update_full_model(self, observations):
        self._bkt = self._bkt.fit(observations)


    @property
    def _current_datetime(self):
        return state_db.get(state_db.Keys.CURRENT_DATETIME)

    @property
    def _am_checkin_time(self):
        return state_db.get(state_db.Keys.AM_CHECKIN_TIME)

    @property
    def _am_checkin_datetime(self):
        return self._put_time_to_datetime(self._am_checkin_time, self._current_datetime)

    @property
    def _pm_checkin_time(self):
        return state_db.get(state_db.Keys.PM_CHECKIN_TIME)

    @property
    def _pm_checkin_datetime(self):
        return self._put_time_to_datetime(self._pm_checkin_time, self._current_datetime)

    @property
    def _is_done_am_checkin_today(self):
        return state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY)

    @property
    def _is_done_pm_checkin_today(self):
        return state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY)

    @property
    def _is_missed_pm_yesterday(self):
        return state_db.get(state_db.Keys.IS_MISSED_PM_YESTERDAY)

    @property
    def _is_missed_am_checkin(self):
        return (
                not state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY)
                and self._current_datetime > self._am_checkin_datetime +
                datetime.timedelta(minutes=self._mins_after_checkin_allowed)
        )

    @property
    def _mins_before_checkin_allowed(self):
        return param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)

    @property
    def _mins_after_checkin_allowed(self):
        return param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    @property
    def _steps_today(self):
        return state_db.get(state_db.Keys.STEPS_TODAY)

    @property
    def _goal_today(self):
        return state_db.get(state_db.Keys.STEPS_GOAL)

    @property
    def _automaticity(self):
        return self._bkt.get_automaticity()

    @property
    def _max_ii_questions(self):
        return param_db.get(param_db.Keys.MAX_NUM_QUESTIONS)


    @property
    def _bkt(self) -> Bkt:
        pL = state_db.get(state_db.Keys.BKT_pL)
        pT = state_db.get(state_db.Keys.BKT_pT)
        pS = state_db.get(state_db.Keys.BKT_pS)
        pG = state_db.get(state_db.Keys.BKT_pG)

        return Bkt(pL0=pL, pT=pT, pS=pS, pG=pG)

    @_bkt.setter
    def _bkt(self, bkt: Bkt):

        if type(bkt) is not Bkt:
            raise ValueError

        pL, pT, pS, pG = bkt.get_params()
        state_db.set(state_db.Keys.BKT_pL, pL)
        state_db.set(state_db.Keys.BKT_pT, pT)
        state_db.set(state_db.Keys.BKT_pS, pS)
        state_db.set(state_db.Keys.BKT_pG, pG)

    @staticmethod
    def _put_time_to_datetime(time, datetime_):
        return datetime_.replace(hour=time.hour, minute=time.minute)


def _is_during_checkin_time_window(time, checkin_datetime, mins_before_allowed, mins_after_allowed):
    start = checkin_datetime - datetime.timedelta(minutes=mins_before_allowed)
    end = checkin_datetime + datetime.timedelta(minutes=mins_after_allowed)
    return _is_in_range(start, end, time)


def _is_in_range(start, end, time):
    return time in DateTimeRange(start_datetime=start, end_datetime=end)

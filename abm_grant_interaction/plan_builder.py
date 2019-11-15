from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.bkt.bkt import Bkt
from abm_grant_interaction.interactions import \
    AmCheckin, PmCheckin, Common, FirstMeeting, OffCheckin, Options, \
    possible_plans
from interaction_engine.planner import MessagerPlanner
import datetime
import math
import random


class PlanBuilder:

    def __init__(self):
        pass

    def build(self):
        planner = MessagerPlanner(possible_plans)

        if self._is_first_meeting():
            planner.insert(
                FirstMeeting.first_meeting,
                post_hook=self._set_first_meeting_to_current_time,
            )
        else:
            planner.insert(Common.Messages.greeting)

            if self._is_missed_checkin():
                planner.insert(Common.Messages.missed_checkin)

            if self._is_am_checkin():
                planner = self._build_am_checkin(planner)
            elif self._is_pm_checkin():
                planner = self._build_pm_checkin(planner)

            planner.insert(Common.Messages.closing)

        return planner

    def _set_first_meeting_to_current_time(self):
        state_db.set(
            state_db.Keys.FIRST_MEETING,
            self._current_datetime,
        )

    def _build_am_checkin(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)
        planner.insert(AmCheckin.Messages.set_goal)

        num_ii_qs = self.get_num_ii_questions(
            self._max_ii_questions,
            self._automaticity,
        )
        questions = []
        for _ in range(num_ii_qs):
            questions.append(
                random.choice([
                    AmCheckin.where_graph,
                    AmCheckin.Messages.when_question,
                    random.choice([
                        AmCheckin.how_busy_graph,
                        AmCheckin.how_remember_graph,
                        AmCheckin.how_motivated_graph,
                    ])
                ])
            )
        for _ in range(self._max_ii_questions-num_ii_qs):
            questions.append(AmCheckin.Messages.big_5_question)

        planner.insert(questions)
        return planner

    def get_num_ii_questions(self, max_qs, automaticity):
        if not (0 <= automaticity <= 1):
            raise ValueError("Automaticity should be between 0-1")
        return max(math.ceil((max_qs+1)*(1-automaticity))-1, 0)

    def _build_pm_checkin(self, planner=None):

        if planner is None:
            planner = MessagerPlanner(possible_plans)

        if self._is_met_steps_goal_today():
            planner.insert(PmCheckin.success_graph)
        else:
            planner.insert(PmCheckin.fail_graph)

        return planner

    def _bkt_update_pL(self, observations):
        self._bkt = self._bkt.update(observations)

    def _bkt_update_full_model(self, observations):
        self._bkt = self._bkt.fit(observations)

    def _is_first_meeting(self):
        return not state_db.is_set(state_db.Keys.FIRST_MEETING)

    def _is_am_checkin(self):
        return self._is_time_to_checkin(
            self._last_am_checkin,
            self._am_checkin_time,
            self._mins_before_checkin_allowed,
            self._mins_after_checkin_allowed
        )

    def _is_pm_checkin(self):
        return self._is_time_to_checkin(
            self._last_pm_checkin,
            self._pm_checkin_time,
            self._mins_before_checkin_allowed,
            self._mins_after_checkin_allowed
        )

    def _is_time_to_checkin(self, last_checkin, set_time, mins_before, mins_after):

        if last_checkin.date() == self._current_datetime.date():
            return False

        if _is_time_within_range(
                set_time,
                self._current_datetime,
                mins_before=mins_before,
                mins_after=mins_after,
        ):
            return True
        else:
            return False

    def _is_missed_am(self):
        return self._is_missed_checkin(
            self._am_checkin_time,
            self._mins_after_checkin_allowed,
            self._last_am_checkin,
        )

    def _is_missed_pm(self):
        return self._is_missed_checkin(
            self._pm_checkin_time,
            self._mins_after_checkin_allowed,
            self._last_pm_checkin,
        )

    def _is_missed_checkin(self, checkin_time, time_after_allowed, last_checkin):
        checkin_datetime = _put_time_to_datetime(checkin_time, self._current_datetime)
        return not (
                checkin_datetime + datetime.timedelta(minutes=time_after_allowed) > self._current_datetime
                and last_checkin.date() != self._current_datetime.date()
        )

    def _is_met_steps_goal_today(self):
        return self._steps_today >= self._goal_today

    @property
    def _current_datetime(self):
        return state_db.get(state_db.Keys.CURRENT_DATETIME)

    @property
    def _am_checkin_time(self):
        return state_db.get(state_db.Keys.AM_CHECKIN_TIME)

    @property
    def _pm_checkin_time(self):
        return state_db.get(state_db.Keys.PM_CHECKIN_TIME)

    @property
    def _last_am_checkin(self):
        return state_db.get(state_db.Keys.LAST_AM_CHECKIN)

    @property
    def _last_pm_checkin(self):
        return state_db.get(state_db.Keys.LAST_PM_CHECKIN)

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


def _is_time_within_range(time, reference_datetime, mins_before, mins_after):
    time_datetime = _put_time_to_datetime(time, reference_datetime)
    return (
            reference_datetime + datetime.timedelta(minutes=mins_after)
            >=
            time_datetime
            >=
            reference_datetime - datetime.timedelta(minutes=mins_before)
    )


def _put_time_to_datetime(time, datetime_):
    return datetime_.replace(hour=time.hour, minute=time.minute)


if __name__ == '__main__':

    planner_ = PlanBuilder().build()
    for p in planner_.plan:
        print(p)

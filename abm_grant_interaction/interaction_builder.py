from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.bkt.bkt import Bkt
from abm_grant_interaction.interactions import \
    AmCheckin, PmCheckin, Common, FirstMeeting, OffCheckin, Options, \
    possible_plans
from interaction_engine.planner import MessagerPlanner
import datetime


def build_plan(is_stochastic=False):
    planner = MessagerPlanner(possible_plans)

    if _is_first_meeting():
        planner.insert(
            FirstMeeting.first_meeting,
            post_hook=_set_first_meeting_to_current_time,
        )
    else:
        planner.insert(Common.Messages.greeting)

        if _is_missed_checkin():
            planner.insert(Common.Messages.missed_checkin)

        if _is_am_checkin():
            planner = _build_am_checkin(planner)
        elif _is_pm_checkin():
            planner = _build_pm_checkin(planner)

        planner.insert(Common.Messages.closing)

    return planner


def _is_first_meeting():
    return not state_db.is_set(state_db.Keys.FIRST_MEETING)


def _set_first_meeting_to_current_time():
    state_db.set(
        state_db.Keys.FIRST_MEETING,
        _current_datetime()
    )


def _is_missed_checkin():
    last_am_checkin = state_db.get(state_db.Keys.LAST_AM_CHECKIN)
    last_pm_checkin = state_db.get(state_db.Keys.LAST_PM_CHECKIN)
    mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    if (
            (
                    _current_datetime() > last_am_checkin + datetime.timedelta(minutes=mins_after_allowed) and
                    last_am_checkin.date() != _current_datetime().date()
            ) or (
            _current_datetime() > last_am_checkin + datetime.timedelta(minutes=mins_after_allowed) and
            last_am_checkin.date() != _current_datetime().date()
    )
    ):
        pass


def _is_missed_generic_checkin(checkin_time, time_after_allowed, last_checkin):
    checkin_datetime = _put_time_to_datetime(checkin_time, _current_datetime())
    return not (
        checkin_datetime + datetime.timedelta(minutes=time_after_allowed) > _current_datetime()
        and last_checkin.date() != _current_datetime().date()
    )


def _is_am_checkin():
    last_am_checkin = state_db.get(state_db.Keys.LAST_AM_CHECKIN)
    am_checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
    mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    return _is_checkin(last_am_checkin, am_checkin_time, mins_before_allowed, mins_after_allowed)


def _is_pm_checkin():

    last_pm_checkin = state_db.get(state_db.Keys.LAST_PM_CHECKIN)
    pm_checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
    mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    return _is_checkin(last_pm_checkin, pm_checkin_time, mins_before_allowed, mins_after_allowed)


def _is_checkin(last_checkin, set_time, mins_before, mins_after):

    if last_checkin.date() == _current_datetime().date():
        return False

    if _is_time_within_range(
            set_time,
            _current_datetime(),
            mins_before=mins_before,
            mins_after=mins_after,
    ):
        return True
    else:
        return False


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


def _build_am_checkin(planner):
    return planner


def _build_pm_checkin(planner=None):

    if planner is None:
        planner = MessagerPlanner(possible_plans)

    if _is_met_steps_goal_today():
        planner.insert(PmCheckin.success_graph)
    else:
        planner.insert(PmCheckin.fail_graph)

    return planner


def _is_met_steps_goal_today():
    return (
            state_db.get(state_db.Keys.STEPS_TODAY)
            >=
            state_db.get(state_db.Keys.STEPS_GOAL)
    )


def _current_datetime():
    return state_db.get(
        state_db.Keys.CURRENT_DATETIME
    )


def _bkt_update_pL(observations):
    bkt = _get_bkt()
    bkt = bkt.update(observations)
    _save_bkt(bkt)


def _bkt_update_full_model(observations):
    bkt = _get_bkt()
    bkt = bkt.fit(observations)
    _save_bkt(bkt)


def _get_automaticity():
    bkt = _get_bkt()
    return bkt.get_automaticity()


def _get_bkt() -> Bkt:
    pL = state_db.get(state_db.Keys.BKT_pL)
    pT = state_db.get(state_db.Keys.BKT_pT)
    pS = state_db.get(state_db.Keys.BKT_pS)
    pG = state_db.get(state_db.Keys.BKT_pG)

    return Bkt(pL0=pL, pT=pT, pS=pS, pG=pG)


def _save_bkt(bkt: Bkt):

    if type(bkt) is not Bkt:
        raise ValueError

    pL, pT, pS, pG = bkt.get_params()
    state_db.set(state_db.Keys.BKT_pL, pL)
    state_db.set(state_db.Keys.BKT_pT, pT)
    state_db.set(state_db.Keys.BKT_pS, pS)
    state_db.set(state_db.Keys.BKT_pG, pG)


if __name__ == '__main__':

    planner_ = build_plan()
    for p in planner_.plan:
        print(p)

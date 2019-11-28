from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import possible_plans
from abm_grant_interaction.goal_setter import GoalSetter

from interaction_engine import InteractionEngine
from interaction_engine.interfaces import TerminalInterface

from abm_grant_interaction.plan_builder.builder import PlanBuilder
import datetime
import schedule


class AbmInteraction:

    def __init__(
            self,
            current_datetime=None,
            interface=None,
            is_reset_state_db=False,
    ):

        if is_reset_state_db:
            state_db.reset()

        if current_datetime is None:
            if state_db.is_set(state_db.Keys.CURRENT_DATETIME):
                current_datetime = self._current_datetime
            else:
                current_datetime = datetime.datetime.now()
        self._current_datetime = current_datetime

        self._plan_builder = PlanBuilder()
        if interface is None:
            self._interface = TerminalInterface(state_db)

        if state_db.is_set(state_db.Keys.FIRST_MEETING):
            start_date = state_db.get(state_db.Keys.FIRST_MEETING)
        else:
            start_date = self._current_datetime-datetime.timedelta(days=7)

        self._goal_setter = GoalSetter(
            client_id=
            param_db.get(param_db.Keys.FITBIT_CLIENT_ID),
            client_secret=
            param_db.get(param_db.Keys.FITBIT_CLIENT_SECRET),
            start_date=start_date,
            min_steps_for_entry_to_be_active=
            param_db.get(param_db.Keys.STEPS_PER_MINUTE_FOR_ACTIVE),
            max_contiguous_non_active_entries_for_continuous_session=
            param_db.get(param_db.Keys.CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK),
            min_consecutive_active_entries_to_count_as_activity=
            param_db.get(param_db.Keys.ACTIVE_MINS_TO_REGISTER_ACTIVITY),
            num_weeks=
            param_db.get(param_db.Keys.WEEKS_WITH_ROBOT),
            final_week_goal=
            param_db.get(param_db.Keys.FINAL_STEPS_GOAL),
            min_weekly_steps_goal=
            param_db.get(param_db.Keys.MIN_WEEKLY_STEPS_GOAL),
            week_goal_min_improvement_ratio=1.1,
            week_goal_max_improvement_ratio=2.0,
            daily_goal_min_to_max_ratio=2.5,
        )

        self._update_week_steps_and_goals()
        self._checkin_scheduler = schedule.Scheduler()
        self._update_scheduler = schedule.Scheduler()

        mins_to_update = param_db.get(param_db.Keys.FITBIT_PULL_RATE_MINS)
        self._update_scheduler.every().day.at("02:00").do(self._new_day_update)
        self._update_scheduler.every(mins_to_update).minutes.do(self._update_todays_steps)

        if state_db.is_set(state_db.Keys.FIRST_MEETING):
            self._build_checkin_schedule()
            state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)
        else:
            self._init_vars()

    def run(self):
        while True:
            self._run_once()

    def _init_vars(self):
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)

    def _handle_prompted(self):
        if self._plan_builder.is_am_checkin() or self._plan_builder.is_pm_checkin():
            self._checkin_scheduler.next_run()
        else:
            self._run_once()

    def _run_once(self, current_time=datetime.datetime.now()):

        self._current_datetime = current_time

        plan = self._plan_builder.build()
        interaction_engine = InteractionEngine(self._interface, plan, possible_plans)
        interaction_engine.run()

        if state_db.get(state_db.Keys.IS_REDO_SCHEDULE):
            self._build_checkin_schedule()
            state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)

    def _build_checkin_schedule(self):

        am_checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
        pm_checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)

        self._checkin_scheduler.clear()
        self._checkin_scheduler.every().day.at(self._time_to_schedule_str(am_checkin_time)).do(self._run_once)
        self._checkin_scheduler.every().day.at(self._time_to_schedule_str(pm_checkin_time)).do(self._run_once)

    def _time_to_schedule_str(self, time):
        return time.strftime("%H:%M")

    def _update_todays_steps(self):
        state_db.set(
            state_db.Keys.STEPS_TODAY,
            self._goal_setter.get_total_active_steps(self._current_datetime)
        )

    def _new_day_update(self):
        self._update_week_steps_and_goals()
        if not state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY):
            state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, True)
        else:
            state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)

        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)

    def _update_week_steps_and_goals(self):
        date = self._current_datetime
        day_goal = self._goal_setter.get_day_goal(date)
        steps_last_week = self._goal_setter.get_steps_last_week(date)
        steps_this_week = self._goal_setter.get_steps_this_week(date)

        state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, day_goal)
        state_db.set(state_db.Keys.STEPS_LAST_WEEK, steps_last_week)
        state_db.set(state_db.Keys.STEPS_THIS_WEEK, steps_this_week)

    @property
    def _current_datetime(self):
        return state_db.get(state_db.Keys.CURRENT_DATETIME)

    @_current_datetime.setter
    def _current_datetime(self, value):
        state_db.set(state_db.Keys.CURRENT_DATETIME, value)


def make_date_time(hour, minute, days=None):
    dt = datetime.datetime.now().replace(hour=hour, minute=minute)
    if days is not None:
        dt += datetime.timedelta(days=days)

    return dt


if __name__ == '__main__':

    IS_RESET_STATE_DB = False
    interaction = AbmInteraction(is_reset_state_db=IS_RESET_STATE_DB)
    mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
    mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)
    if 0:
        print("FIRST INTERACTION")
        interaction._run_once(current_time=make_date_time(8, 0, days=0))
        print(state_db)

    print("OFF CHECKIN")
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=0)
    )

    print("PM CHECKIN - Fail")
    interaction._update_todays_steps()
    state_db.set(
        state_db.Keys.STEPS_TODAY,
        state_db.get(state_db.Keys.STEPS_GOAL) - 1
    )
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=0)
    )

    print("OFF CHECKIN")
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=0)
    )

    print("Early AM CHECKIN - low automaticity")
    interaction._new_day_update()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=1)
        - datetime.timedelta(minutes=mins_before_allowed-1)
    )

    print("Early PM CHECKIN - Success")
    interaction._update_todays_steps()
    state_db.set(
        state_db.Keys.STEPS_TODAY,
        state_db.get(state_db.Keys.STEPS_GOAL) + 1
    )
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=1)
                     - datetime.timedelta(minutes=mins_before_allowed-1)
    )

    print("Late AM - medium automaticity")
    interaction._new_day_update()
    state_db.set(state_db.Keys.BKT_pL, 0.5)
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=2)
                     + datetime.timedelta(minutes=mins_after_allowed-1)
    )

    print("Early PM CHECKIN")
    interaction._update_todays_steps()
    checkin_time = datetime.time(23, 55)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=2)
    )

    print("OFF CHECKIN missed am")
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=0)
    )

    print("PM CHECKIN missed AM")
    interaction._new_day_update()
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=3)
    )

    print("AM CHECKIN - high automaticity")
    interaction._new_day_update()
    state_db.set(state_db.Keys.BKT_pL, 0.75)
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=4)
    )

    print("AM CHECKIN missed PM")
    interaction._new_day_update()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    interaction._run_once(
        current_time=make_date_time(checkin_time.hour, checkin_time.minute, days=5)
    )
    print(state_db)

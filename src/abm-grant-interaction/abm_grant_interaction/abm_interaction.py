#! /bin/python3.6

import rospy
from std_msgs.msg import Bool, Float32

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import possible_plans
from abm_grant_interaction.goal_setter.setter import GoalSetter

from interaction_engine import InteractionEngine
from interaction_engine.interfaces import TerminalClientAndServerInterface

from abm_grant_interaction.plan_builder.builder import PlanBuilder
import datetime
import schedule
from freezegun import freeze_time
import logging

from abm_fitbit_client import AbmFitbitClient


logging.basicConfig(level=logging.INFO)


class AbmInteraction:

    def __init__(
            self,
            credentials_file_path="fitbit_credentials.yaml",
            redirect_url="http://localhost",
            is_data_recording_topic='data_capture/is_record',
            automaticity_topic='abm/automaticity',
            interface=None,
            is_reset_state_db=False,
            goal_setter=None,
    ):

        if is_reset_state_db:
            logging.info("Reseting database")
            state_db.reset()

        self._plan_builder = PlanBuilder()
        if interface is None:
            interface = TerminalClientAndServerInterface(state_db)
        self._interface = interface
        self._fitbit = AbmFitbitClient(
            credentials_file_path=credentials_file_path,
            redirect_url=redirect_url,
        )

        start_days_before_first_meeting = datetime.timedelta(days=7)
        if state_db.is_set(state_db.Keys.FIRST_MEETING):
            start_date = state_db.get(state_db.Keys.FIRST_MEETING)-start_days_before_first_meeting
        else:
            start_date = datetime.datetime.now()-start_days_before_first_meeting

        if goal_setter is None:
            logging.info('Creating goal setter')
            goal_setter = GoalSetter(
                fitbit_active_steps_fn=self._fitbit.get_total_steps,
                start_date=start_date,
                num_weeks=param_db.get(param_db.Keys.WEEKS_WITH_ROBOT)+1,  # +1 for week with just fitbit
                final_week_goal=
                param_db.get(param_db.Keys.FINAL_STEPS_GOAL),
                min_weekly_steps_goal=
                param_db.get(param_db.Keys.MIN_WEEKLY_STEPS_GOAL),
                week_goal_min_improvement_ratio=1.1,
                week_goal_max_improvement_ratio=2.0,
                daily_goal_min_to_max_ratio=2.5,
            )
        self._goal_setter = goal_setter

        self._is_recording_publisher = rospy.Publisher(is_data_recording_topic, Bool, queue_size=1)
        self._automaticity_publisher = rospy.Publisher(automaticity_topic, Float32, queue_size=1)

        self._update_week_steps_and_goals()
        self._update_todays_steps()

        self._checkin_scheduler = schedule.Scheduler()

        self._update_scheduler = schedule.Scheduler()
        self._update_scheduler.every(15).seconds.do(self._new_day_update)

        self._is_prompt_to_run = False
        if state_db.is_set(state_db.Keys.FIRST_MEETING):
            self._build_checkin_schedule()
            state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)
        else:
            self._init_vars()

    def run_scheduler_once(self):
        self._update_scheduler.run_pending()

        if not state_db.is_set(state_db.Keys.FIRST_MEETING) or self._is_prompt_to_run:
            self._update_todays_steps()
            self._build_and_run_plan()
            self._is_prompt_to_run = False
        else:
            self._checkin_scheduler.run_pending()

    def set_prompt_to_handle(self):
        self._is_prompt_to_run = True

    def _init_vars(self):
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)
        state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)
        state_db.set(state_db.Keys.LAST_DAY_UPDATE_DATE, datetime.datetime.now().date())

    def _run_scheduled_if_still_open(self):
        if self._plan_builder.is_am_checkin() or self._plan_builder.is_pm_checkin():
            self._update_todays_steps()
            self._build_and_run_plan()

    def _build_and_run_plan(self):
        plan = self._plan_builder.build()
        interaction_engine = InteractionEngine(self._interface, plan, possible_plans)
        try:
            self._publish_is_record_msg(True)
            interaction_engine.run()
        except TimeoutError:
            pass
        finally:
            self._publish_is_record_msg(False)

        if state_db.get(state_db.Keys.IS_REDO_SCHEDULE):
            self._build_checkin_schedule()
            state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)
    
    def _publish_is_record_msg(self, is_record: bool):
        msg = Bool()
        msg.data = is_record
        if is_record is True:
            rospy.loginfo("Published to start recording data")
        else:
            rospy.loginfo("Published to stop recording data")
        self._is_recording_publisher.publish(msg)

    def _build_checkin_schedule(self):

        am_checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
        pm_checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)

        self._checkin_scheduler.clear()
        self._checkin_scheduler.every().day.at(
            self._time_to_schedule_str(am_checkin_time)).do(self._run_scheduled_if_still_open)
        self._checkin_scheduler.every().day.at(
            self._time_to_schedule_str(pm_checkin_time)).do(self._run_scheduled_if_still_open)

    def _time_to_schedule_str(self, time):
        return time.strftime("%H:%M")

    def _update_todays_steps(self):
        state_db.set(
            state_db.Keys.STEPS_TODAY,
            self._fitbit.get_total_steps(datetime.datetime.now().date())
        )
        logging.info('Updated steps today')
        state_db.set(
            state_db.Keys.LAST_FITBIT_SYNC,
            self._fitbit.get_last_sync()
        )
        logging.info('Updated last sync time')

    def _new_day_update(self):

        last_day_update = state_db.get(state_db.Keys.LAST_DAY_UPDATE_DATE)
        current_date = datetime.datetime.now().date()
        days_since_last_day_update = (current_date-last_day_update).days

        if days_since_last_day_update > 0:

            self._update_week_steps_and_goals()
            if not state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY):
                state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, True)
            else:
                state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)

            self._publish_automaticity()

            state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
            state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)

            state_db.set(state_db.Keys.LAST_DAY_UPDATE_DATE, datetime.datetime.now().date())

    def _publish_automaticity(self):
        automaticity = state_db.get(state_db.Keys.BKT_pL)
        rospy.loginfo("Publishing automaticity: {}".format(automaticity))
        self._automaticity_publisher.publish(
            Float32(
                automaticity
            )
        )

    def _update_week_steps_and_goals(self):
        date = datetime.datetime.now()
        day_goal = self._goal_setter.get_day_goal(date)
        logging.info('Updating steps')
        steps_last_week = self._goal_setter.get_steps_last_week(date)
        logging.info('Updated  steps last weeky')
        steps_this_week = self._goal_setter.get_steps_this_week(date)
        logging.info('Updated  steps this weeky')

        state_db.set(state_db.Keys.MIN_SUGGESTED_STEPS_TODAY, round(day_goal))
        state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, round(1.3*day_goal))
        state_db.set(state_db.Keys.MAX_SUGGESTED_STEPS_TODAY, round(2*day_goal))
        state_db.set(state_db.Keys.STEPS_LAST_WEEK, steps_last_week)
        state_db.set(state_db.Keys.STEPS_THIS_WEEK, steps_this_week)


if __name__ == '__main__' and False:

    IS_RESET_STATE_DB = False
    interaction = AbmInteraction(is_reset_state_db=IS_RESET_STATE_DB)
    mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
    mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    print("FIRST INTERACTION")
    with freeze_time("2019-11-1 8:05:00"):
        interaction._build_and_run_plan()

    print("OFF CHECKIN")
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-1 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("PM CHECKIN - Fail")
    interaction._update_todays_steps()
    state_db.set(
        state_db.Keys.STEPS_TODAY,
        state_db.get(state_db.Keys.STEPS_GOAL) - 1
    )
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    with freeze_time(f"2019-11-1 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("OFF CHECKIN")
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    with freeze_time(f"2019-11-1 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("Early AM CHECKIN - low automaticity")
    interaction._new_day_update()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-2 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00") as frozen_datetime:
        frozen_datetime.tick(delta=datetime.timedelta(minutes=mins_before_allowed-1))
        interaction._build_and_run_plan()

    print("Early PM CHECKIN - Success")
    interaction._update_todays_steps()
    state_db.set(
        state_db.Keys.STEPS_TODAY,
        state_db.get(state_db.Keys.STEPS_GOAL) + 1
    )
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    with freeze_time(f"2019-11-2 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00") as frozen_datetime:
        frozen_datetime.tick(delta=datetime.timedelta(minutes=mins_before_allowed-1))
        interaction._build_and_run_plan()

    print("Late AM - medium automaticity")
    interaction._new_day_update()
    state_db.set(state_db.Keys.BKT_pL, 0.5)
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-3 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00") as frozen_datetime:
        frozen_datetime.tick(delta=datetime.timedelta(minutes=mins_after_allowed-1))
        interaction._build_and_run_plan()

    print("Late PM CHECKIN")
    interaction._update_todays_steps()
    checkin_time = datetime.time(23, 55)
    with freeze_time(f"2019-11-3 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("OFF CHECKIN missed am")
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-4 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00") as frozen_datetime:
        frozen_datetime.tick(delta=datetime.timedelta(minutes=mins_after_allowed+1))
        interaction._build_and_run_plan()

    print("PM CHECKIN missed AM")
    interaction._new_day_update()
    interaction._update_todays_steps()
    checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
    with freeze_time(f"2019-11-4 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("AM CHECKIN - high automaticity")
    interaction._new_day_update()
    state_db.set(state_db.Keys.BKT_pL, 0.75)
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-5 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

    print("AM CHECKIN missed PM")
    interaction._new_day_update()
    checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
    with freeze_time(f"2019-11-6 {checkin_time.hour:02d}:{checkin_time.minute:02d}:00"):
        interaction._build_and_run_plan()

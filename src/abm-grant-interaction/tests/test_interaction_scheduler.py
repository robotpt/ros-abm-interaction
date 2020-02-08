import unittest
from unittest import mock

from abm_grant_interaction.abm_interaction import AbmInteraction

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import possible_plans
from abm_grant_interaction.goal_setter import GoalSetter
from abm_grant_interaction.testing_utils.simulate_messages import \
    simulate_run_plan, simulate_run_once
from freezegun import freeze_time

import datetime


class TestAbmInteraction(unittest.TestCase):

    def setUp(self) -> None:

        fitbit_patcher = mock.patch('abm_grant_interaction.abm_interaction.AbmFitbitClient')
        self._mock_fitbit = fitbit_patcher.start()
        self._mock_fitbit.return_value.get_last_sync.side_effect = lambda: datetime.datetime.now()
        self.set_steps_per_day(300)

        run_once_patcher = mock.patch('abm_grant_interaction.abm_interaction.AbmInteraction._build_and_run_plan')
        self._mock_run_once = run_once_patcher.start()
        self._mock_run_once.side_effect = self.build_and_simulate_plan

        state_db.reset()
        self.abm_interaction = AbmInteraction()
        self.mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
        self.mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    def set_steps_per_day(self, value):
        self._mock_fitbit.return_value.get_total_steps.return_value = value

    def build_and_simulate_plan(self):
        plan = self.abm_interaction._plan_builder.build()
        simulate_run_plan(plan)

    def update_after_first_meeting(self):
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, datetime.time(8, 30))
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, datetime.time(20, 30))
        state_db.set(state_db.Keys.DAY_OFF, 'saturday')
        state_db.set(state_db.Keys.USER_NAME, 'John')
        state_db.set(state_db.Keys.STEPS_GOAL, state_db.get(state_db.Keys.SUGGESTED_STEPS_TODAY))

        self.abm_interaction._build_checkin_schedule()
        state_db.set(state_db.Keys.IS_REDO_SCHEDULE, False)

    def update_after_am_checkin(self):
        state_db.set(state_db.Keys.STEPS_GOAL, state_db.get(state_db.Keys.SUGGESTED_STEPS_TODAY))

    def update_day_steps(self, steps_diff_from_goal=0):
        self.set_steps_per_day(
            state_db.get(state_db.Keys.STEPS_GOAL) + steps_diff_from_goal
        )
        self.abm_interaction._update_todays_steps()

    def test_check_first_run(self):

        self.assertFalse(state_db.is_set(state_db.Keys.FIRST_MEETING))
        self.abm_interaction.set_prompt_to_handle()
        self.abm_interaction.run_scheduler_once()
        self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))
        self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
        self.assertFalse(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))

    def test_prompt_interactions(self):
        """
        Note that the steps goals and numbers get in a weird positive feedback loop because of how I
        monkey patched the fitbit reader
        """

        num_days = param_db.get(param_db.Keys.WEEKS_WITH_ROBOT)*7

        initial_datetime = datetime.datetime(
            year=2019, month=1, day=1, hour=8, minute=6, second=3
        )
        with freeze_time(initial_datetime) as frozen_datetime:
            state_db.reset()
            self.abm_interaction = AbmInteraction()

            self.update_after_first_meeting()

            pm_checkin_datetime = self.get_pm_checkin_datetime(0, initial_datetime)
            frozen_datetime.move_to(pm_checkin_datetime)
            self.update_day_steps()
            self.abm_interaction.set_prompt_to_handle()
            self.abm_interaction.run_scheduler_once()
            self.update_after_am_checkin()

            self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))
            self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
            self.assertTrue(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))
            self.assertTrue(state_db.get(state_db.Keys.IS_MET_GOAL))

            for day in range(1, num_days + 2):

                am_checkin_datetime = self.get_am_checkin_datetime(day, initial_datetime)
                frozen_datetime.move_to(am_checkin_datetime)
                self.abm_interaction._new_day_update()
                self.abm_interaction.set_prompt_to_handle()
                self.abm_interaction.run_scheduler_once()
                self.update_after_am_checkin()

                # Run non consequential off-checkin
                for _ in range(2):
                    self.abm_interaction.set_prompt_to_handle()
                    self.abm_interaction.run_scheduler_once()

                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
                self.assertFalse(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))

                pm_checkin_datetime = self.get_pm_checkin_datetime(day, initial_datetime)
                frozen_datetime.move_to(pm_checkin_datetime)
                self.update_day_steps()
                self.abm_interaction.set_prompt_to_handle()
                self.abm_interaction.run_scheduler_once()

                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))
                self.assertTrue(state_db.get(state_db.Keys.IS_MET_GOAL))

                # Run non consequential off-checkin
                for _ in range(2):
                    self.abm_interaction._build_and_run_plan()

    def test_scheduler_for_updates_and_running_full_interaction(self):
        """
        Note that the steps goals and numbers get in a weird positive feedback loop because of how I
        monkey patched the fitbit reader
        """

        num_days = param_db.get(param_db.Keys.WEEKS_WITH_ROBOT)*7

        initial_datetime = datetime.datetime(
            year=2019, month=1, day=1, hour=8, minute=6, second=3
        )
        with freeze_time(initial_datetime) as frozen_datetime:
            state_db.reset()
            self.abm_interaction = AbmInteraction()

            self.update_after_first_meeting()

            pm_checkin_datetime = self.get_pm_checkin_datetime(0, initial_datetime)
            frozen_datetime.move_to(pm_checkin_datetime)
            self.update_day_steps()
            self.abm_interaction.run_scheduler_once()
            self.update_after_am_checkin()

            self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))
            self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
            self.assertTrue(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))
            self.assertTrue(state_db.get(state_db.Keys.IS_MET_GOAL))

            for day in range(1, num_days + 2):

                # Make sure that the system updates automatically
                am_checkin_datetime = self.get_am_checkin_datetime(day, initial_datetime)
                frozen_datetime.move_to(am_checkin_datetime - datetime.timedelta(minutes=2*self.mins_before_allowed))
                self.abm_interaction.run_scheduler_once()
                self.assertFalse(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
                self.assertFalse(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))

                # Run non consequential off-checkin
                for _ in range(2):
                    self.abm_interaction.set_prompt_to_handle()
                    self.abm_interaction.run_scheduler_once()

                # Run AM checkin
                frozen_datetime.move_to(am_checkin_datetime)
                self.abm_interaction.run_scheduler_once()
                self.update_after_am_checkin()
                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
                self.assertFalse(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))

                # Run non consequential off-checkin
                for _ in range(2):
                    self.abm_interaction.set_prompt_to_handle()
                    self.abm_interaction.run_scheduler_once()

                # Run PM checkin
                pm_checkin_datetime = self.get_pm_checkin_datetime(day, initial_datetime)
                frozen_datetime.move_to(pm_checkin_datetime)
                self.update_day_steps()
                self.abm_interaction.run_scheduler_once()

                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY))
                self.assertTrue(state_db.get(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY))
                self.assertTrue(state_db.get(state_db.Keys.IS_MET_GOAL))

                # Run non consequential off-checkin
                for _ in range(2):
                    self.abm_interaction.set_prompt_to_handle()
                    self.abm_interaction.run_scheduler_once()

    @staticmethod
    def get_pm_checkin_datetime(day, initial_datetime):
        pm_checkin_time = state_db.get(state_db.Keys.PM_CHECKIN_TIME)
        pm_checkin_date_time = (
            (
                    initial_datetime
                    + datetime.timedelta(days=day)
            ).replace(
                hour=pm_checkin_time.hour,
                minute=pm_checkin_time.minute,
            )
        )
        return pm_checkin_date_time

    @staticmethod
    def get_am_checkin_datetime(day, initial_datetime):
        am_checkin_time = state_db.get(state_db.Keys.AM_CHECKIN_TIME)
        am_checkin_date_time = (
            (
                    initial_datetime
                    + datetime.timedelta(days=day)
            ).replace(
                hour=am_checkin_time.hour,
                minute=am_checkin_time.minute,
            )
        )
        return am_checkin_date_time


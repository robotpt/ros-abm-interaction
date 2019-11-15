from abm_grant_interaction import plan_builder
from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import \
    AmCheckin, PmCheckin, Common, FirstMeeting, OffCheckin, Options, \
    possible_plans

from interaction_engine.planner import MessagerPlanner

import unittest
import datetime


"""
Process
0. Reset state_db
1. Set entries in state_db to bring a specific state
2. Build expected plan
3. Check for equality of plan
"""


def simulate_run_plan(plan):
    while plan.is_active:
        simulate_run_once(plan)


def simulate_run_once(plan):

    message_name, pre_hook, post_hook = plan.pop_plan(is_return_hooks=True)

    pre_hook()
    post_hook()


class TestPlanBuilder(unittest.TestCase):

    def setUp(self) -> None:

        state_db.reset()

        self.true_plan = MessagerPlanner(possible_plans)
        self.builder = plan_builder.PlanBuilder()

    def test_select_first_meeting(self):
        self.true_plan.insert(FirstMeeting.first_meeting)

        resulting_plan = self.builder.build()
        self.assertEqual(self.true_plan, resulting_plan)

        self.assertFalse(state_db.is_set(state_db.Keys.FIRST_MEETING))
        state_db.set(state_db.Keys.CURRENT_DATETIME, datetime.datetime.now())
        simulate_run_plan(resulting_plan)
        self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))

    def test_build_pm_with_goal_met(self):
        self.true_plan.insert(PmCheckin.success_graph)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.STEPS_GOAL, 100)
        state_db.set(state_db.Keys.STEPS_TODAY, 200)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        self.assertEqual(
            self.true_plan,
            self.builder._build_pm_checkin()
        )

    def test_build_pm_with_goal_fail(self):
        self.true_plan.insert(PmCheckin.fail_graph)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.STEPS_GOAL, 200)
        state_db.set(state_db.Keys.STEPS_TODAY, 100)
        self.assertEqual(
            self.true_plan,
            self.builder._build_pm_checkin()
        )

    def test_get_num_implementation_intention_questions_to_ask(self):
        max_num_qs = 3
        for automaticity, truth_num_qs in [
            (0, 3),
            (0.01, 3),
            (0.1, 3),
            (0.24, 3),
            (0.26, 2),
            (0.49, 2),
            (0.51, 1),
            (0.74, 1),
            (0.76, 0),
            (0.99, 0),
            (1.0, 0),
        ]:
            self.assertEqual(
                truth_num_qs,
                self.builder.get_num_ii_questions(max_num_qs, automaticity)
            )

        for automaticity in [-1, -.01, 1.01, 2]:
            self.assertRaises(
                ValueError,
                self.builder.get_num_ii_questions,
                max_num_qs,
                automaticity
            )

    def test_is_checkin(self):

        am_hour, am_minute = 8, 0
        am_checkin_time = datetime.time(am_hour, am_minute)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, am_checkin_time)

        pm_hour, pm_minute = 18, 30
        pm_checkin_time = datetime.time(pm_hour, pm_minute)
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, pm_checkin_time)

        for days in range(1, 10):
            last_checkin = datetime.datetime.now().replace(hour=am_hour, minute=am_minute) - \
                           datetime.timedelta(days=days)
            state_db.set(state_db.Keys.LAST_AM_CHECKIN, last_checkin)
            state_db.set(state_db.Keys.LAST_PM_CHECKIN, last_checkin)

            mins_before_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)
            mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

            for d_minute in [
                0,
                -mins_before_allowed,
                mins_after_allowed,
            ]:
                am_current_datetime = datetime.datetime.now().replace(
                    hour=am_hour, minute=am_minute
                )
                am_current_datetime -= datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, am_current_datetime)
                self.assertTrue(self.builder._is_am_checkin())

                pm_current_datetime = datetime.datetime.now().replace(
                    hour=pm_hour, minute=pm_minute
                )
                pm_current_datetime -= datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, pm_current_datetime)
                self.assertTrue(self.builder._is_pm_checkin())

            for d_minute in [
                -mins_before_allowed-1,
                mins_after_allowed+1,
                -mins_before_allowed-100,
                mins_after_allowed+100,
            ]:
                am_current_datetime = datetime.datetime.now().replace(
                    hour=am_hour, minute=am_minute
                )
                am_current_datetime += datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, am_current_datetime)
                is_am = self.builder._is_am_checkin()
                self.assertFalse(is_am)

                pm_current_datetime = datetime.datetime.now().replace(
                    hour=pm_hour, minute=pm_minute
                )
                pm_current_datetime += datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, pm_current_datetime)
                is_pm = self.builder._is_pm_checkin()
                self.assertFalse(is_pm)

    def test_try_am_with_last_checkin_today(self):

        hour, minute = 8, 0
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, checkin_time)
        current_datetime = datetime.datetime.now().replace(hour=hour, minute=minute)

        last_checkin = datetime.datetime.now().replace(hour=hour, minute=minute) - \
                       datetime.timedelta(days=0)

        state_db.set(state_db.Keys.LAST_AM_CHECKIN, last_checkin)

        state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)
        self.assertFalse(self.builder._is_am_checkin())

    def test_try_pm_with_last_checkin_today(self):

        hour, minute = 18, 30
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, checkin_time)
        current_datetime = datetime.datetime.now().replace(hour=hour, minute=minute)

        last_checkin = datetime.datetime.now().replace(hour=hour, minute=minute) - \
                       datetime.timedelta(days=0)

        state_db.set(state_db.Keys.LAST_PM_CHECKIN, last_checkin)

        state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)
        self.assertFalse(self.builder._is_pm_checkin())

    def test_missed_checkin(self):
        hour, minute = 18, 30
        checkin_time = datetime.time(hour, minute)
        time_after_allowed = 15
        last_checkin = datetime.datetime.now().replace(hour=hour, minute=minute) - \
                       datetime.timedelta(days=1)
        for i in range(time_after_allowed):
            current_datetime = datetime.datetime.now().replace(hour=hour, minute=minute+i)
            state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)

            self.assertFalse(
                self.builder._is_missed_checkin(checkin_time, time_after_allowed, last_checkin)
            )
        for i in range(time_after_allowed, 2*time_after_allowed):
            current_datetime = datetime.datetime.now().replace(hour=hour, minute=minute+i)
            state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)

            self.assertTrue(
                self.builder._is_missed_checkin(checkin_time, time_after_allowed, last_checkin)
            )

    def test_get_set_bkt(self):

        pL0, pT0, pS0, pG0 = self.builder._bkt.get_params()

        observations = [True, False, True, True, False]

        self.builder._bkt_update_pL(observations)
        pL1, pT1, pS1, pG1 = self.builder._bkt.get_params()
        self.assertNotEqual(pL0, pL1)
        self.assertEqual(pT0, pT1)
        self.assertEqual(pS0, pS1)
        self.assertEqual(pG0, pG1)

        pL1_, pT1_, pS1_, pG1_ = self.builder._bkt.get_params()
        self.assertEqual(pL1, pL1_)
        self.assertEqual(pT1, pT1_)
        self.assertEqual(pS1, pS1_)
        self.assertEqual(pG1, pG1_)

        self.builder._bkt_update_full_model(observations)
        pL2, pT2, pS2, pG2 = self.builder._bkt.get_params()
        self.assertNotEqual(pL1, pL2)
        self.assertNotEqual(pT1, pT2)
        self.assertNotEqual(pS1, pS2)
        self.assertNotEqual(pG1, pG2)

    def test_bkt_operations(self):
        automaticity = self.builder._automaticity
        # True because of adding epsilon to make not degenerate
        self.assertLessEqual(
            state_db.get(state_db.Keys.BKT_pL),
            automaticity
        )

        old_pL = automaticity
        for _ in range(100):
            self.builder._bkt_update_pL(True)
            new_pL = self.builder._automaticity
            self.assertLessEqual(old_pL, new_pL)
            old_pL = new_pL
        self.assertLess(automaticity, old_pL)

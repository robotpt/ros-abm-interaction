from abm_grant_interaction import interaction_builder as builder
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


class TestInteractionBuilder(unittest.TestCase):

    def setUp(self) -> None:

        state_db.reset()

        self.true_plan = MessagerPlanner(possible_plans)

    def test_select_first_meeting(self):
        self.true_plan.insert(FirstMeeting.first_meeting)

        resulting_plan = builder.build_plan()
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
            builder._build_pm_checkin()
        )

    def test_build_pm_with_goal_fail(self):
        self.true_plan.insert(PmCheckin.fail_graph)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.STEPS_GOAL, 200)
        state_db.set(state_db.Keys.STEPS_TODAY, 100)
        self.assertEqual(
            self.true_plan,
            builder._build_pm_checkin()
        )

    def test_build_am_at_all(self):
        self.true_plan.insert(
            [
                AmCheckin.Messages.set_goal,
            ]
        )
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())

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
                self.assertTrue(builder._is_am_checkin())

                pm_current_datetime = datetime.datetime.now().replace(
                    hour=pm_hour, minute=pm_minute
                )
                pm_current_datetime -= datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, pm_current_datetime)
                self.assertTrue(builder._is_pm_checkin())

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
                is_am = builder._is_am_checkin()
                self.assertFalse(is_am)

                pm_current_datetime = datetime.datetime.now().replace(
                    hour=pm_hour, minute=pm_minute
                )
                pm_current_datetime += datetime.timedelta(minutes=d_minute)
                state_db.set(state_db.Keys.CURRENT_DATETIME, pm_current_datetime)
                is_pm = builder._is_pm_checkin()
                self.assertFalse(is_pm)

    def test_try_am_with_last_checkin_today(self):

        hour, minute = 8, 0
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, checkin_time)
        current_datetime = datetime.datetime.now().replace(
        )

        last_checkin = datetime.datetime.now().replace(hour=hour, minute=minute) - \
                       datetime.timedelta(days=0)

        state_db.set(state_db.Keys.LAST_AM_CHECKIN, last_checkin)

        state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)
        self.assertFalse(builder._is_am_checkin())

    def test_try_pm_with_last_checkin_today(self):

        hour, minute = 18, 30
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, checkin_time)
        current_datetime = datetime.datetime.now().replace(
        )

        last_checkin = datetime.datetime.now().replace(hour=hour, minute=minute) - \
                       datetime.timedelta(days=0)

        state_db.set(state_db.Keys.LAST_PM_CHECKIN, last_checkin)

        state_db.set(state_db.Keys.CURRENT_DATETIME, current_datetime)
        self.assertFalse(builder._is_pm_checkin())

    def test_get_set_bkt(self):

        bkt1 = builder._get_bkt()
        pL0, pT0, pS0, pG0 = bkt1.get_params()

        observations = [True, True, True, True, False]
        bkt1 = bkt1.update(observations)

        pL1, pT1, pS1, pG1 = bkt1.get_params()
        self.assertNotEqual(pL0, pL1)
        self.assertEqual(pT0, pT1)
        self.assertEqual(pS0, pS1)
        self.assertEqual(pG0, pG1)
        builder._save_bkt(bkt1)

        bkt2 = builder._get_bkt()
        pL1_, pT1_, pS1_, pG1_ = bkt2.get_params()
        self.assertEqual(pL1, pL1_)
        self.assertEqual(pT1, pT1_)
        self.assertEqual(pS1, pS1_)
        self.assertEqual(pG1, pG1_)

        bkt1 = bkt1.fit(observations)
        pL2, pT2, pS2, pG2 = bkt1.get_params()
        self.assertNotEqual(pL1, pL2)
        self.assertNotEqual(pT1, pT2)
        self.assertNotEqual(pS1, pS2)
        self.assertNotEqual(pG1, pG2)

        bkt3 = builder._get_bkt()
        pL2_, pT2_, pS2_, pG2_ = bkt3.get_params()
        self.assertNotEqual(pL2, pL2_)
        self.assertNotEqual(pT2, pT2_)
        self.assertNotEqual(pS2, pS2_)
        self.assertNotEqual(pG2, pG2_)

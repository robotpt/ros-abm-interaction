from abm_grant_interaction.plan_builder import builder
from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import \
    PmCheckin, Common, FirstMeeting, possible_plans
from freezegun import freeze_time

from interaction_engine.planner import MessagerPlanner
from interaction_engine.messager import DirectedGraph, Message

import unittest
import datetime


def simulate_run_plan(plan):
    while plan.is_active:
        simulate_run_once(plan)


messagers = dict()
for m in possible_plans:
    messagers[m.name] = m


def simulate_run_once(plan, is_populate_messages=False):

    message_name, pre_hook, post_hook = plan.pop_plan(is_return_hooks=True)

    pre_hook()
    if is_populate_messages:
        populate_messages(message_name)
    post_hook()


def populate_messages(message_name):
    messager = messagers[message_name]
    if type(messager) is Message:
        messages = [messager]
    elif type(messager) is DirectedGraph:
        messages = []
        for node in messager.get_nodes():
            messages.append(messager.get_message(node))
    for message in messages:
        message.content
        message.options


class TestPlanBuilder(unittest.TestCase):

    def setUp(self) -> None:

        state_db.reset()

        self.true_plan = MessagerPlanner(possible_plans)
        self.builder = builder.PlanBuilder()

    def test_select_first_meeting(self):
        self.true_plan.insert(FirstMeeting.first_meeting)

        self.assertFalse(state_db.is_set(state_db.Keys.FIRST_MEETING))
        resulting_plan = self.builder.build()
        self.assertEqual(self.true_plan, resulting_plan)
        simulate_run_plan(resulting_plan)
        self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))

    def test_build_pm_with_goal_met(self):
        self.true_plan.insert(
            [
                PmCheckin.success_graph,
            ]
        )
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.STEPS_GOAL, 100)
        state_db.set(state_db.Keys.STEPS_TODAY, 200)
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        self.assertEqual(
            self.true_plan,
            self.builder._build_pm_checkin()
        )

    def test_build_pm_with_goal_fail(self):
        self.true_plan.insert(
            [
                PmCheckin.fail_graph,
            ]
        )
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.FIRST_MEETING, datetime.datetime.now())
        state_db.set(state_db.Keys.STEPS_GOAL, 200)
        state_db.set(state_db.Keys.STEPS_TODAY, 100)
        self.assertEqual(
            self.true_plan,
            self.builder._build_pm_checkin()
        )

    def test_run_am(self):

        state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, 300)
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
        state_db.set(state_db.Keys.IS_MISSED_PM_YESTERDAY, False)

        hour, minute = 8, 0
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, checkin_time)

        with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):
            self.assertTrue(self.builder.is_am_checkin())

            plan = self.builder._build_am_checkin()
            for _ in range(len(plan.plan)-1):
                simulate_run_once(plan)
                self.assertTrue(self.builder.is_am_checkin())
            simulate_run_once(plan)
            self.assertFalse(self.builder.is_am_checkin())

    def test_run_pm(self):
        am_hour, am_minute = 8, 0
        am_checkin_time = datetime.time(am_hour, am_minute)
        state_db.set(state_db.Keys.AM_CHECKIN_TIME, am_checkin_time)

        hour, minute = 18, 0
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, checkin_time)
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)

        with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):

            self.assertFalse(self.builder.is_am_checkin())

            state_db.set(state_db.Keys.STEPS_TODAY, 300)
            state_db.set(state_db.Keys.STEPS_GOAL, 600)

            self.assertTrue(self.builder.is_pm_checkin())
            plan = self.builder._build_pm_checkin()
            for _ in range(len(plan.plan)-1):
                simulate_run_once(plan)
                self.assertTrue(self.builder.is_pm_checkin())
            simulate_run_once(plan)
            self.assertFalse(self.builder.is_pm_checkin())

    def test_run_pm_updates_bkt(self):

        hour, minute = 18, 0
        checkin_time = datetime.time(hour, minute)
        state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, checkin_time)
        state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)

        with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):

            self.assertTrue(self.builder.is_pm_checkin())

            for _ in range(10):
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
                state_db.set(state_db.Keys.STEPS_TODAY, 100)
                state_db.set(state_db.Keys.STEPS_GOAL, 20)
                plan = self.builder._build_pm_checkin()
                pL_old = self.builder._bkt.get_automaticity()
                simulate_run_plan(plan)
                pL_new = self.builder._bkt.get_automaticity()
                self.assertLessEqual(pL_old, pL_new)

            for _ in range(10):
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
                state_db.set(state_db.Keys.STEPS_TODAY, 10)
                state_db.set(state_db.Keys.STEPS_GOAL, 20)
                plan = self.builder._build_pm_checkin()
                pL_old = self.builder._bkt.get_automaticity()
                simulate_run_plan(plan)
                pL_new = self.builder._bkt.get_automaticity()
                self.assertGreaterEqual(pL_old, pL_new)

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
                self.builder._get_num_ii_questions(max_num_qs, automaticity)
            )

        for automaticity in [-1, -.01, 1.01, 2]:
            self.assertRaises(
                ValueError,
                self.builder._get_num_ii_questions,
                max_num_qs,
                automaticity
            )

    def test_is_time_for_status_update(self):
        am_checkin_hour = 8
        am_checkin_min = 40
        pm_checkin_hour = 18
        pm_checkin_min = 21

        assert pm_checkin_hour - 1 > am_checkin_hour

        state_db.set(state_db.Keys.AM_CHECKIN_TIME, datetime.time(am_checkin_hour, am_checkin_min))
        state_db.set(state_db.Keys.PM_CHECKIN_TIME, datetime.time(pm_checkin_hour, pm_checkin_min))

        for hour, minute in [
            (0, 0),
            (am_checkin_hour-1%24, am_checkin_min%60),
            (am_checkin_hour%24, am_checkin_min-1%60),
            (am_checkin_hour%24, am_checkin_min%60),
            (am_checkin_hour%24, am_checkin_min+1%60),
            (am_checkin_hour+1%24, am_checkin_min%60),
            (pm_checkin_hour-1%24, pm_checkin_min%60),
            (pm_checkin_hour%24, pm_checkin_min-1%60),
        ]:
            with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
                self.assertFalse(
                    self.builder._is_time_for_status_update()
                )

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
                self.assertTrue(
                    self.builder._is_time_for_status_update()
                )

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, True)
                self.assertFalse(
                    self.builder._is_time_for_status_update()
                )

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, True)
                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, True)
                self.assertFalse(
                    self.builder._is_time_for_status_update()
                )

    def test_is_pm_checkin_window(self):

        pm_checkin_hour = 18
        pm_checkin_min = 21

        state_db.set(state_db.Keys.PM_CHECKIN_TIME, datetime.time(pm_checkin_hour, pm_checkin_min))

        for hour, minute in [
            (pm_checkin_hour%24, pm_checkin_min%60),
            (pm_checkin_hour%24, pm_checkin_min+1%60),
            (23, 55),
        ]:
            with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):

                state_db.set(state_db.Keys.IS_DONE_PM_CHECKIN_TODAY, False)
                self.assertTrue(
                    self.builder.is_pm_checkin()
                )

    def test_is_missed_am(self):

        am_checkin_hour = 8
        am_checkin_min = 40

        state_db.set(state_db.Keys.AM_CHECKIN_TIME, datetime.time(am_checkin_hour, am_checkin_min))

        for hour, minute in [
            (0, 0),
            (am_checkin_hour-1%24, am_checkin_min%60),
            (am_checkin_hour%24, am_checkin_min-1%60),
            (am_checkin_hour%24, am_checkin_min%60),
            (am_checkin_hour%24, am_checkin_min+1%60),
        ]:
            with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59"):

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
                self.assertFalse(
                    self.builder._is_missed_am_checkin
                )

        time_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)
        for hour, minute in [
            (am_checkin_hour%24, am_checkin_min+1%60),
            (am_checkin_hour+1%24, am_checkin_min%60),
            (am_checkin_hour+1%24, am_checkin_min+1%60),
        ]:
            with freeze_time(f"2011-11-1 {hour:02d}:{minute:02d}:59") as frozen_datetime:
                frozen_datetime.tick(delta=datetime.timedelta(minutes=time_after_allowed))

                state_db.set(state_db.Keys.IS_DONE_AM_CHECKIN_TODAY, False)
                self.assertTrue(
                    self.builder._is_missed_am_checkin
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


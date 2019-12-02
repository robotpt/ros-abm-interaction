import unittest
from unittest import mock

from abm_grant_interaction.interaction import AbmInteraction

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import possible_plans
from abm_grant_interaction.goal_setter import GoalSetter
from abm_grant_interaction.testing_utils.simulate_messages import \
    simulate_run_plan, simulate_run_once



class TestAbmInteraction(unittest.TestCase):

    def setUp(self) -> None:

        self.mock_goal_setter = mock.Mock(spec=GoalSetter)
        self.mock_goal_setter.get_day_goal.return_value = 300
        self.mock_goal_setter.get_steps_last_week.return_value = 2500
        self.mock_goal_setter.get_steps_this_week.return_value = 0

        state_db.reset()
        self.abm_interaction = AbmInteraction(
            goal_setter=self.mock_goal_setter,
        )
        self.mins_before_allowed = param_db.get(param_db.Keys.MINS_BEFORE_ALLOW_CHECKIN)
        self.mins_after_allowed = param_db.get(param_db.Keys.MINS_AFTER_ALLOW_CHECKIN)

    def build_and_simulate_plan(self):
        plan = self.abm_interaction._plan_builder.build()
        simulate_run_plan(plan)

    @mock.patch('abm_grant_interaction.interaction.AbmInteraction._run_once')
    def test_check_first_run(self, mock_run):

        mock_run.side_effect = self.build_and_simulate_plan

        self.assertFalse(state_db.is_set(state_db.Keys.FIRST_MEETING))
        self.abm_interaction.handle_prompt()
        self.assertTrue(state_db.is_set(state_db.Keys.FIRST_MEETING))

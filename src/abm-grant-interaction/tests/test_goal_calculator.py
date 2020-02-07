import unittest
import math

from abm_grant_interaction.goal_setter import goal_functions

num_weeks = 6
weekly_min = 2000
end_weekly_goal = 10000

DAYS_PER_WEEK = 7


class TestCalculateWeekGoal(unittest.TestCase):

    def test_not_reach_minimum_week_goal(self):

        for prev_steps in [0, 100, 500, 1000]:
            for i in reversed(range(1, num_weeks+1)):
                self.assertEqual(
                    weekly_min,
                    goal_functions.get_week_goal(
                        steps_last_week=prev_steps,
                        weeks_remaining=i,
                    )
                )

    def test_reach_goal_leads_to_end_goal(self):

        prev_steps = 0
        steps_goal = None
        for i in reversed(range(1, num_weeks+1)):
            steps_goal = goal_functions.get_week_goal(
                steps_last_week=prev_steps,
                weeks_remaining=i,
            )
            prev_steps = steps_goal

        self.assertAlmostEqual(
            end_weekly_goal,
            steps_goal,
            -2
        )

    def test_exceed_goal(self):

        improve_ratio = 1.5
        prev_steps = 0
        steps_goal = None
        for i in reversed(range(1, num_weeks + 1)):
            steps_goal = goal_functions.get_week_goal(
                steps_last_week=prev_steps,
                weeks_remaining=i,
            )
            prev_steps = improve_ratio*steps_goal
        self.assertLessEqual(
            end_weekly_goal,
            steps_goal
        )

    def test_invalid_weeks_remaining(self):
        for v in [0, -1]:
            self.assertRaises(
                ValueError,
                goal_functions.get_week_goal,
                0,
                v,
                is_raise_exception_at_end_of_study=True,
            )


class TestCalculateDayGoal(unittest.TestCase):

    def test_extra_progress_day_goal(self):

        improvement_ratio = 1.2
        weekly_goal = 2000
        steps_so_far = 0
        goals = []
        for i in range(DAYS_PER_WEEK):
            daily_goal = goal_functions.get_daily_goal(
                weekly_goal,
                steps_so_far=steps_so_far,
                days_remaining=DAYS_PER_WEEK-i,
            )
            steps_so_far += daily_goal*improvement_ratio
            goals.append(daily_goal)

        for i in range(1, len(goals)):
            self.assertGreaterEqual(
                goals[i-1],
                goals[i]
            )

    def test_minimal_progress_day_goal(self):

        weekly_goal = 2000
        steps_so_far = 0
        for i in range(DAYS_PER_WEEK):
            daily_goal = goal_functions.get_daily_goal(
                weekly_goal,
                steps_so_far=steps_so_far,
                days_remaining=DAYS_PER_WEEK-i,
            )
            self.assertAlmostEqual(
                math.ceil(weekly_goal/DAYS_PER_WEEK),
                daily_goal,
                -1
            )
            steps_so_far += daily_goal

    def test_no_progress_day_goal(self):

        weekly_goal = 2000
        steps_so_far = 0
        min_to_max_ratio = 2.5
        truth_min_goal = weekly_goal / DAYS_PER_WEEK
        for i in range(DAYS_PER_WEEK):
            daily_goal = goal_functions.get_daily_goal(
                weekly_goal,
                steps_so_far=steps_so_far,
                days_remaining=DAYS_PER_WEEK - i,
                min_to_max_ratio=min_to_max_ratio
            )
            self.assertTrue(
                0.9*truth_min_goal < daily_goal < 1.1*truth_min_goal*min_to_max_ratio
            )

    def test_invalid_days_remaining(self):
        for v in [0, -1]:
            self.assertRaises(
                ValueError,
                goal_functions.get_daily_goal,
                2000,
                0,
                v
            )

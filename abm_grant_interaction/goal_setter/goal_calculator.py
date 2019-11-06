from abm_grant_interaction.goal_setter import goal_functions


class GoalCalculator:

    def __init__(
            self,
            final_week_goal=10000,
            min_weekly_steps_goal=2000,
            week_goal_min_improvement_ratio=1.1,
            week_goal_max_improvement_ratio=2.0,
            daily_goal_min_to_max_ratio=2.5,
    ):
        self._final_week_goal = final_week_goal
        self._min_weekly_steps_goal = min_weekly_steps_goal
        self._week_goal_min_improvement_ratio = week_goal_min_improvement_ratio
        self._week_goal_max_improvement_ratio = week_goal_max_improvement_ratio
        self._daily_goal_min_to_max_ratio = daily_goal_min_to_max_ratio

    def get_week_goal(
            self,
            steps_last_week,
            weeks_remaining,
    ):
        return goal_functions.get_week_goal(
            steps_last_week,
            weeks_remaining,
            final_week_goal=self._final_week_goal,
            min_weekly_steps_goal=self._min_weekly_steps_goal,
            min_improvement_ratio=self._week_goal_min_improvement_ratio,
            max_improvement_ratio=self._week_goal_max_improvement_ratio,
        )

    def get_day_goal(
            self,
            week_goal,
            steps_so_far,
            days_remaining,
    ):
        return goal_functions.get_daily_goal(
            week_goal,
            steps_so_far,
            days_remaining,
            self._daily_goal_min_to_max_ratio
        )

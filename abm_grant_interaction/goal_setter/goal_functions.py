from robotpt_common_utils import math_tools

import math


def get_week_goal(
        steps_last_week,
        weeks_remaining,
        final_week_goal=10000,
        min_weekly_steps_goal=2000,
        min_improvement_ratio=1.1,
        max_improvement_ratio=2.0,
        is_raise_exception_at_end_of_study=False
):

    if weeks_remaining <= 0:
        if is_raise_exception_at_end_of_study:
            raise ValueError("'weeks_remaining' must be greater than 0")
        else:
            return steps_last_week

    if steps_last_week*max_improvement_ratio < min_weekly_steps_goal:
        return min_weekly_steps_goal

    goal = min_improvement_ratio * steps_last_week
    if goal < final_week_goal:
        d_goal = (final_week_goal - steps_last_week) / weeks_remaining
        goal = steps_last_week + d_goal

    lower_bound = min_weekly_steps_goal
    upper_bound = max_improvement_ratio * steps_last_week
    if upper_bound < lower_bound:
        upper_bound = None

    return math.ceil(
        math_tools.bound(
            goal,
            lower_bound,
            upper_bound
        )
    )


def get_daily_goal(
        week_goal,
        steps_so_far,
        days_remaining,
        min_to_max_ratio=2.5,
):

    if days_remaining <= 0:
        raise ValueError("'days_remaining' must be greater than 0")

    DAYS_PER_WEEK = 7
    min_goal = week_goal / DAYS_PER_WEEK
    max_goal = min_to_max_ratio * min_goal
    return math.ceil(
        math_tools.bound(
            (week_goal - steps_so_far)/days_remaining,
            min_goal,
            max_goal
        )
    )



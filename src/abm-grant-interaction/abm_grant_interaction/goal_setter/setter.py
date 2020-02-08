from abm_grant_interaction.goal_setter import goal_calculator, session_planner

from robotpt_common_utils import lists

import datetime


DAYS_IN_A_WEEK = 7


class GoalSetter:

    def __init__(
            self,
            fitbit_active_steps_fn,
            start_date=datetime.date.today()-datetime.timedelta(days=DAYS_IN_A_WEEK),
            num_weeks=6,
            final_week_goal=10000,
            min_weekly_steps_goal=2000,
            week_goal_min_improvement_ratio=1.1,
            week_goal_max_improvement_ratio=2.0,
            daily_goal_min_to_max_ratio=2.5,
    ):
        self._fitbit_active_steps_fn = fitbit_active_steps_fn
        self._num_weeks = num_weeks
        self._session = session_planner.SessionPlanner(
            start_date,
            DAYS_IN_A_WEEK
        )
        self._goal_calculator = goal_calculator.GoalCalculator(
            final_week_goal,
            min_weekly_steps_goal,
            week_goal_min_improvement_ratio,
            week_goal_max_improvement_ratio,
            daily_goal_min_to_max_ratio,
        )

    def get_week_goal(self, date=datetime.date.today()):

        steps_last_week = self.get_steps_last_week(date)

        return self._goal_calculator.get_week_goal(
            steps_last_week=steps_last_week,
            weeks_remaining=self._get_weeks_remaining(date)
        )

    def get_steps_last_week(self, date):
        dates = self._get_past_weeks_dates(date)
        return self._get_total_active_steps(dates)

    def get_steps_this_week(self, date):
        dates = self._get_this_weeks_dates(date)

        # Don't look at future dates
        dates = [d for d in dates if d <= datetime.datetime.today().date()]

        return self._get_total_active_steps(dates)

    def get_day_goal(self, date=datetime.date.today()):
        week_goal = self.get_week_goal(date)

        dates = self._get_this_weeks_dates(date, until=date)
        steps_so_far = self._get_total_active_steps(dates)

        days_remaining = self._session.get_days_left_in_current_session(date)

        return self._goal_calculator.get_day_goal(
            week_goal=week_goal,
            steps_so_far=steps_so_far,
            days_remaining=days_remaining
        )

    def _get_this_weeks_dates(
            self,
            date=datetime.date.today(),
            until=None,
    ):
        session_number = self._session.get_session_num(date)

        dates = self._session.get_session_date_range(session_number)
        if until is None:
            return dates

        if type(until) is datetime.datetime:
            until = until.date()
        return [date for date in dates if date < until]

    def _get_past_weeks_dates(self, date=datetime.date.today()):
        session_number = self._session.get_session_num(date)
        if session_number > 0:
            return self._session.get_session_date_range(session_number-1)
        else:
            return None

    def _get_total_active_steps(self, dates=None):

        if dates is None:
            return 0

        dates = lists.make_sure_is_iterable(dates)
        steps = 0
        for date in dates:
            steps += self._get_total_active_steps_one_date(date)
        return steps

    def _get_total_active_steps_one_date(self, date):
        return self._fitbit_active_steps_fn(date)

    def _get_weeks_remaining(self, date):
        week_number = self._session.get_session_num(date)
        return self._num_weeks - week_number

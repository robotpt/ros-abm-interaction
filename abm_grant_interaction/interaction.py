from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions import possible_plans
from abm_grant_interaction.goal_setter import GoalSetter

from interaction_engine import InteractionEngine
from interaction_engine.interfaces import TerminalInterface

from abm_grant_interaction.plan_builder.builder import PlanBuilder
import datetime


class AbmInteraction:

    def __init__(self):

        self._goal_setter = GoalSetter(
            client_id=
            param_db.get(param_db.Keys.FITBIT_CLIENT_ID),
            client_secret=
            param_db.get(param_db.Keys.FITBIT_CLIENT_SECRET),
            start_date=self._current_datetime()-datetime.timedelta(days=7),
            min_steps_for_entry_to_be_active=
            param_db.get(param_db.Keys.STEPS_PER_MINUTE_FOR_ACTIVE),
            max_contiguous_non_active_entries_for_continuous_session=
            param_db.get(param_db.Keys.CONSECUTIVE_MINS_INACTIVE_BEFORE_BREAKING_ACTIVITY_STREAK),
            min_consecutive_active_entries_to_count_as_activity=
            param_db.get(param_db.Keys.ACTIVE_MINS_TO_REGISTER_ACTIVITY),
            num_weeks=
            param_db.get(param_db.Keys.WEEKS_WITH_ROBOT),
            final_week_goal=
            param_db.get(param_db.Keys.FINAL_STEPS_GOAL),
            min_weekly_steps_goal=
            param_db.get(param_db.Keys.MIN_WEEKLY_STEPS_GOAL),
            week_goal_min_improvement_ratio=1.1,
            week_goal_max_improvement_ratio=2.0,
            daily_goal_min_to_max_ratio=2.5,
        )

    def update_todays_steps(self):
        state_db.set(
            self._goal_setter.get_total_active_steps(self._current_datetime())
        )

    def update_week_steps_and_goals(self):
        date = self._current_datetime
        day_goal = self._goal_setter.get_day_goal(date)
        steps_last_week = self._goal_setter.get_steps_last_week(date)
        steps_this_week = self._goal_setter.get_steps_this_week(date)

        state_db.set(state_db.Keys.STEPS_GOAL, day_goal)
        state_db.set(state_db.Keys.STEPS_LAST_WEEK, steps_last_week)
        state_db.set(state_db.Keys.STEPS_THIS_WEEK, steps_this_week)

    @property
    def _current_datetime(self):
        return state_db.get(state_db.Keys.CURRENT_DATETIME)


if __name__ == '__main__':

    IS_RESET_DB = True
    if IS_RESET_DB:
        state_db.reset()

    current_datetime = datetime.datetime.now()
    plan_builder = PlanBuilder()
    plan = plan_builder.build()

    interface = TerminalInterface(state_db)
    interaction_engine = InteractionEngine(interface, plan, possible_plans)
    interaction_engine.run()

    print(state_db)

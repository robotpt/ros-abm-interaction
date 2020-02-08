from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.goal_setter.goal_calculator import GoalCalculator
from abm_grant_interaction.interactions.first_meeting import FirstMeeting

from interaction_engine import InteractionEngine
from interaction_engine.planner import MessagerPlanner
from interaction_engine.interfaces import TerminalClientAndServerInterface

possible_plans = [
    FirstMeeting.first_meeting
]

# Create a plan
plan_ = MessagerPlanner(possible_plans)
plan_.insert(FirstMeeting.first_meeting)

steps_last_week = 3000
goal_calc = GoalCalculator()
week_goal = goal_calc.get_week_goal(steps_last_week=steps_last_week, weeks_remaining=6)
day_goal = goal_calc.get_day_goal(week_goal, 0, 7)

state_db.set(state_db.Keys.STEPS_LAST_WEEK, steps_last_week)
state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, day_goal)

ie = InteractionEngine(TerminalClientAndServerInterface(state_db), plan_, possible_plans)
ie.run()

print(state_db)
print(param_db)

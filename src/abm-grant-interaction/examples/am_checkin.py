import datetime

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions.am_checkin import AmCheckin

from interaction_engine import InteractionEngine
from interaction_engine.planner import MessagerPlanner
from interaction_engine.interfaces import TerminalClientAndServerInterface

state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, 600)
state_db.set(state_db.Keys.AM_CHECKIN_TIME, datetime.time(8, 0))
state_db.set(state_db.Keys.PM_CHECKIN_TIME, datetime.time(18, 0))

possible_plans = [
    AmCheckin.Messages.big_5_question,
    AmCheckin.Messages.when_question,
    AmCheckin.Messages.set_goal,
    AmCheckin.where_graph,
    AmCheckin.how_busy_graph,
    AmCheckin.how_motivated_graph,
    AmCheckin.how_remember_graph,
]

# Create a plan
plan_ = MessagerPlanner(possible_plans)
plan_.insert(AmCheckin.Messages.set_goal)
plan_.insert(AmCheckin.where_graph)
plan_.insert(AmCheckin.Messages.when_question)
plan_.insert(AmCheckin.how_busy_graph)
plan_.insert(AmCheckin.how_remember_graph)
plan_.insert(AmCheckin.how_motivated_graph)
for _ in range(3):
    plan_.insert(AmCheckin.Messages.big_5_question)

ie = InteractionEngine(TerminalClientAndServerInterface(state_db), plan_, possible_plans)
ie.run()

print(state_db)
print(param_db)

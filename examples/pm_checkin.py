from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions.pm_checkin import PmCheckin
import datetime

from interaction_engine import InteractionEngine
from interaction_engine.planner import MessagerPlanner
from interaction_engine.interfaces import TerminalInterface

possible_plans = [
    PmCheckin.Messages.no_sync,
    PmCheckin.success_graph,
    PmCheckin.fail_graph
]

steps_today = 300
steps_goal = 600
last_sync = (
        datetime.datetime.now() -
        datetime.timedelta(minutes=param_db.get(param_db.Keys.MINS_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING) + 1)
)

state_db.set(state_db.Keys.LAST_FITBIT_SYNC, last_sync)
state_db.set(state_db.Keys.STEPS_TODAY, steps_today)
state_db.set(state_db.Keys.STEPS_GOAL, steps_goal)

# Create a plan
plan_ = MessagerPlanner(possible_plans)
if (datetime.datetime.now() - last_sync).seconds // 60 > \
        param_db.get(param_db.Keys.MINS_BEFORE_WARNING_ABOUT_FITBIT_NOT_SYNCING):
    plan_.insert(PmCheckin.Messages.no_sync)
else:
    if steps_goal <= steps_today:
        plan_.insert(PmCheckin.success_graph)
    else:
        plan_.insert(PmCheckin.fail_graph)

ie = InteractionEngine(TerminalInterface(state_db), plan_, possible_plans)
ie.run()

print(state_db)
print(param_db)

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.interactions.off_checkin import OffCheckin
from abm_grant_interaction.interactions.options import Options
from abm_grant_interaction.interactions.common import Common

from interaction_engine import InteractionEngine
from interaction_engine.planner import MessagerPlanner
from interaction_engine.interfaces import TerminalInterface

import datetime


state_db.set(state_db.Keys.AM_CHECKIN_TIME, datetime.time(8, 0))
state_db.set(state_db.Keys.PM_CHECKIN_TIME, datetime.time(18, 0))
state_db.set(state_db.Keys.STEPS_TODAY, 300)
state_db.set(state_db.Keys.STEPS_GOAL, 600)

possible_plans = [
    OffCheckin.Messages.give_status,
    Options.options,
    Common.Messages.greeting,
    Common.Messages.closing,
]

# Create a plan
plan_ = MessagerPlanner(possible_plans)
plan_.insert(Common.Messages.greeting)
plan_.insert(OffCheckin.Messages.give_status)
plan_.insert(Options.options)
plan_.insert(Common.Messages.closing)

ie = InteractionEngine(TerminalInterface(state_db), plan_, possible_plans)
ie.run()

print(state_db)
print(param_db)

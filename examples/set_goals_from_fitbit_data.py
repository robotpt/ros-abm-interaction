from abm_grant_interaction.goal_setter import GoalSetter
from abm_grant_interaction import param_db


client_id_ = param_db.get(param_db.Keys.FITBIT_CLIENT_ID)
client_secret_ = param_db.get(param_db.Keys.FITBIT_CLIENT_SECRET)

goal_setter = GoalSetter(
    client_id=client_id_,
    client_secret=client_secret_,
)

goal = goal_setter.get_week_goal()
print(f"Week goal: {goal}")

goal = goal_setter.get_day_goal()
print(f"Day goal: {goal}")


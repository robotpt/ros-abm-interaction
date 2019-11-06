from abm_grant_interaction.goal_setter import GoalSetter
import yaml


secrets_file = 'secrets.yaml'

with open(secrets_file, 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

client_id_ = data['client_id']
client_secret_ = data['client_secret']

goal_setter = GoalSetter(
    client_id=client_id_,
    client_secret=client_secret_,
)

goal = goal_setter.get_week_goal()
print(f"Week goal: {goal}")

goal = goal_setter.get_day_goal()
print(f"Day goal: {goal}")


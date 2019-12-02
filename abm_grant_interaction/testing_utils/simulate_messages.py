from abm_grant_interaction.interactions import \
    PmCheckin, Common, FirstMeeting, possible_plans

from interaction_engine.messager import DirectedGraph, Message


def simulate_run_plan(plan):
    while plan.is_active:
        simulate_run_once(plan)


messagers = dict()
for m in possible_plans:
    messagers[m.name] = m


def simulate_run_once(plan, is_populate_messages=False):

    message_name, pre_hook, post_hook = plan.pop_plan(is_return_hooks=True)

    pre_hook()
    if is_populate_messages:
        populate_messages(message_name)
    post_hook()


def populate_messages(message_name):
    messager = messagers[message_name]
    if type(messager) is Message:
        messages = [messager]
    elif type(messager) is DirectedGraph:
        messages = []
        for node in messager.get_nodes():
            messages.append(messager.get_message(node))
    for message in messages:
        message.content
        message.options

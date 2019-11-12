from interaction_engine.messager import Message, Node, DirectedGraph, most_recent_options_graph
from abm_grant_interaction import state_db, param_db, text_populator
from robotpt_common_utils import lists

import datetime


def _get_last_n_list(list_, n, exclude_values=None):
    exclude_values = lists.make_sure_is_iterable(exclude_values)
    list_ = lists.remove_repeats(list_, is_remove_from_front=False)
    out = []
    idx = len(list_)-1
    while len(out) < n and idx >= 0:
        value = list_[idx]
        if value not in exclude_values:
            out.append(value)
        idx -= 1

    return out


class Common:

    class Nodes:
        greeting_morning = Node(
            name='greeting',
            content="{greeting_morning}",
            options="{greeting_morning}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_convert_from_str_fn=str,
            text_populator=text_populator,
            transitions='exit'
        )
        greeting = Node(
            name='greeting',
            content="{greeting}",
            options="{greeting}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_convert_from_str_fn=str,
            text_populator=text_populator,
            transitions='exit'
        )

    class Graphs:
        pass


class AmCheckin:

    class Messages:

        greeting = Message(
            content="{greeting_morning}",
            options="{greeting_morning}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_convert_from_str_fn=str,
            text_populator=text_populator,
        )
        closing = Message(
            content="Bye",
            options=['Bye', 'See ya!'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_convert_from_str_fn=str,
            text_populator=text_populator,
        )
        big_5_question = Message(
            content=(
                    "How do you feel about the following statement? " +
                    "'{'var': 'big_5_question', 'index': " +
                    "'{'db': '%s', 'post-op': 'increment'}'}'" % state_db.Keys.PSYCH_QUESTION_INDEX
            ),
            options=[
                'Strongly agree',
                'Agree',
                'Neutral',
                'disagree',
                'Strongly disagree',
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_db_key=state_db.Keys.PSYCH_QUESTION_ANSWERS,
            is_append_result=True,
            text_populator=text_populator,
        )
        when_question = Message(
            content="When will you walk today?",
            options='is when',
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.WALK_TIME,
            result_convert_from_str_fn=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=lambda x: datetime.datetime.now().time() < x < state_db.get(state_db.Keys.PM_CHECKIN_TIME),
            error_message="Please pick a time after now and before our evening checkin",
            is_confirm=True,
            text_populator=text_populator,
        )

    where_graph = most_recent_options_graph(
        "Where do you want to walk?",
        options=lambda: state_db.get(state_db.Keys.WALK_PLACES),
        max_num_options=param_db.get(param_db.Keys.NUM_WHERE_OPTIONS),
        save_db_key=state_db.Keys.WALK_PLACES,
        text_populator=text_populator,
        new_entry_text_choice='Somewhere else',
        new_entry_message="So where will you walk?",
        new_entry_options="Is where",
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )
    how_remember_graph = most_recent_options_graph(
        "How will you remember to walk?",
        options=lambda: state_db.get(state_db.Keys.WALK_PLACES),
        max_num_options=param_db.get(param_db.Keys.NUM_WHERE_OPTIONS),
        save_db_key=state_db.Keys.WALK_PLACES,
        text_populator=text_populator,
        new_entry_text_choice='Somewhere else',
        new_entry_message="So where will you walk?",
        new_entry_options="Is where",
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )


if __name__ == '__main__':

    from interaction_engine import InteractionEngine
    from interaction_engine.planner import MessagerPlanner
    from interaction_engine.interfaces import TerminalInterface

    graphs_ = [
        AmCheckin.Messages.greeting,
        AmCheckin.Messages.closing,
        AmCheckin.Messages.big_5_question,
        AmCheckin.Messages.when_question,
        AmCheckin.where_graph,
    ]

    # Create a plan
    plan_ = MessagerPlanner(graphs_)
    plan_.insert(AmCheckin.where_graph)
    plan_.insert(AmCheckin.Messages.greeting)
    plan_.insert(AmCheckin.Messages.when_question)
    for _ in range(3):
        plan_.insert(AmCheckin.Messages.big_5_question)
    plan_.insert(AmCheckin.Messages.closing)

    ie = InteractionEngine(TerminalInterface(state_db), plan_, graphs_)
    ie.run()

    print(state_db)
    print(param_db)


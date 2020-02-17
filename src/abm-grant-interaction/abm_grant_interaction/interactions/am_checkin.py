from interaction_engine.messager import Message, most_recent_options_graph
from abm_grant_interaction import state_db, param_db, text_populator

import datetime


class AmCheckin:

    class Messages:

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
            content="{when_question}",
            options='is when',
            message_type=Message.Type.TIME_ENTRY,
            args=[
                '15',
                lambda: "{'db': '%s'}" % state_db.Keys.WALK_TIME,
            ],
            result_db_key=state_db.Keys.WALK_TIME,
            result_convert_from_str_fn=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=lambda x: (
                state_db.get(state_db.Keys.AM_CHECKIN_TIME) <= x <= state_db.get(state_db.Keys.PM_CHECKIN_TIME)
            ),
            error_message="Please pick a time after now and before our evening checkin",
            text_populator=text_populator,
        )
        set_goal = Message(
            content=(
                "I suggest that you do {'db': '%s'} steps today. " % state_db.Keys.SUGGESTED_STEPS_TODAY +
                "How many steps would you like to do today?"
            ),
            options='steps',
            args=[
                lambda: "{'db': '%s'}" % state_db.Keys.MIN_SUGGESTED_STEPS_TODAY,
                lambda: "{'db': '%s'}" % state_db.Keys.MAX_SUGGESTED_STEPS_TODAY,
                '1',
                lambda: "{'db': '%s'}" % state_db.Keys.SUGGESTED_STEPS_TODAY,
            ],
            message_type=Message.Type.SLIDER,
            result_convert_from_str_fn=int,
            result_db_key=state_db.Keys.STEPS_GOAL,
            tests=lambda x: x >= state_db.get(state_db.Keys.MIN_SUGGESTED_STEPS_TODAY),
            error_message=(
                "Please select a goal that is at least {'db': '%s'} steps" % state_db.Keys.MIN_SUGGESTED_STEPS_TODAY,
            ),
            text_populator=text_populator,
        )

    where_graph = most_recent_options_graph(
        "ask where",
        "{where_question}",
        options=lambda: state_db.get(state_db.Keys.WALK_PLACES),
        max_num_options=param_db.get(param_db.Keys.NUM_OPTIONS_TO_DISPLAY),
        save_db_key=state_db.Keys.WALK_PLACES,
        text_populator=text_populator,
        new_entry_text_choice='Somewhere else',
        new_entry_message="So where will you walk?",
        new_entry_options="Is where",
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )
    how_remember_graph = most_recent_options_graph(
        "how_remember",
        "{how_question_forget}",
        options=lambda: state_db.get(state_db.Keys.HOW_REMEMBER),
        max_num_options=param_db.get(param_db.Keys.NUM_OPTIONS_TO_DISPLAY),
        save_db_key=state_db.Keys.HOW_REMEMBER,
        text_populator=text_populator,
        new_entry_text_choice='Something else',
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )
    how_busy_graph = most_recent_options_graph(
        "how_busy",
        "{how_question_busy}",
        options=lambda: state_db.get(state_db.Keys.HOW_BUSY),
        max_num_options=param_db.get(param_db.Keys.NUM_OPTIONS_TO_DISPLAY),
        save_db_key=state_db.Keys.HOW_BUSY,
        text_populator=text_populator,
        new_entry_text_choice='Something else',
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )
    how_motivated_graph = most_recent_options_graph(
        "how_motivated",
        "{how_question_not_motivated}",
        options=lambda: state_db.get(state_db.Keys.HOW_MOTIVATE),
        max_num_options=param_db.get(param_db.Keys.NUM_OPTIONS_TO_DISPLAY),
        save_db_key=state_db.Keys.HOW_MOTIVATE,
        text_populator=text_populator,
        new_entry_text_choice='Something else',
        tests=lambda x: len(x) > 1,
        new_entry_error_message="Please write more than one letter"
    )

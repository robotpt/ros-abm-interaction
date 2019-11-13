from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class PmCheckin:

    class Messages:
        no_sync = Message(
            content=(
                "I haven't heard from your Fitbit in a while. " +
                "Try syncing your phone, and then check back with me again."
            ),
            options=[
                "{affirmative_plus_button_response}",
                "{Ill_try_that_button_response}",
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )

    success_graph = DirectedGraph(
        name='success',
        start_node='start',
        nodes=[
            Node(
                name='start',
                content=(
                        "{your_goal_was_to_do} {'db': '%s'} steps{today_or_not} " % state_db.Keys.STEPS_GOAL +
                        "and you've done {'db': '%s'} steps. " % state_db.Keys.STEPS_TODAY +
                        "{congratulations_steps_goal}"
                ),
                options=[
                    '{thanks_means_a_lot}',
                    '{thank_you}',
                ],
                transitions='exit',
                message_type=Message.Type.MULTIPLE_CHOICE,
                text_populator=text_populator,
            ),
        ],
    )
    fail_graph = DirectedGraph(
        name='fail',
        start_node='start',
        nodes=[
            Node(
                name='start',
                content=(
                    "{your_goal_was_to_do} {'db': '%s'} steps{today_or_not} " % state_db.Keys.STEPS_GOAL +
                    "and you've done {'db': '%s'} steps. " % state_db.Keys.STEPS_TODAY +
                    "{too_bad_didnt_reach_steps_goal}"
                ),
                options=[
                    'Okay',
                    'Oops',
                    'About that...'
                ],
                message_type=Message.Type.MULTIPLE_CHOICE,
                transitions='why',
                text_populator=text_populator,
            ),
            Node(
                name='why',
                content='{question_failed_goal}',
                options=[
                    "I was too busy",
                    "I forgot",
                    "I didn't feel like it",
                    "I didn't feel well",
                    "Something else",
                ],
                result_db_key=state_db.Keys.FAIL_WHY,
                is_append_result=True,
                message_type=Message.Type.MULTIPLE_CHOICE,
                transitions=['explain fail']*3 + ['feel better'] + ['explain fail'],
                text_populator=text_populator,
            ),
            Node(
                name='explain fail',
                content='{transitional_statement} Can you explain?',
                options="is why",
                result_db_key=state_db.Keys.FAIL_WHY,
                is_append_result=True,
                message_type=Message.Type.DIRECT_INPUT,
                transitions='encourage',
                text_populator=text_populator,
            ),
            Node(
                name='feel better',
                content='Ok, I understand. I hope you feel better.',
                options=['{thank_you}'],
                message_type=Message.Type.MULTIPLE_CHOICE,
                transitions='encourage',
                text_populator=text_populator,
            ),
            Node(
                name='encourage',
                content='{transitional_statement} {encourage_after_fail}',
                options=['{positive_failure}', '{neutral_failure}', '{apologize_failure}'],
                message_type=Message.Type.MULTIPLE_CHOICE,
                transitions='exit',
                text_populator=text_populator,
            )
        ],
    )



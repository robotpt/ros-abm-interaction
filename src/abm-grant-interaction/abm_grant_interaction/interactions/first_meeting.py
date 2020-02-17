from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator

from abm_grant_interaction.interactions.options import Options

import datetime


class FirstMeeting:

    class Messages:
        introduce_self = Message(
            content=(
                    "Nice to meet you, {'db': '%s'}. " % state_db.Keys.USER_NAME +
                    "My name is QT. I'm a robot made by LuxAI in Luxembourg, a country in Europe. " +
                    "I'm going to try to help you walk more regularly. " +
                    "I won't go on walks with you*wink*. " +
                    "Instead, I'll ask you questions about your plans to walk and " +
                    "keep track of your daily steps by wirelessly talking to your Fitbit watch. "
            ),
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
            options=['Sure thing!', 'Sure', 'No thanks'],
        )
        explain_checkin = Message(
            content=(
                    "To help you walk regularly, we'll talk at least twice a day: " +
                    "once in the morning and once in the evening. " +
                    "In the morning, we'll set a walking goal for the day and I'll ask you some questions. " +
                    "These questions will be about your plans to walk or about you. " +
                    "In the evening, we'll review the day. If you don't meet your walking goal, I may ask you why. "
            ),
            options='Sounds good',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        explain_off_checkin = Message(
            content=(
                "You can also talk to me any other time. " +
                # "I'll be happy to see you. *nod* I can tell you jokes or tell you good things. " +
                # "You can ask me to introduce myself, if you'd like me to meet someone new. " +
                # "I can also explain how we'll work together again. " +
                "Lastly, you can change what I call you or when we have our morning and evening checkins. "
            ),
            options='Okay',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        explain_fitbit = Message(
            content=(
                    "Now, I'll tell you about how I'll work with your Fitbit watch. " +
                    "This part is important.*nod* " +
                    "To know how much you walk, I'll talk to your Fitbit watch. " +
                    "Unfortunately, this can take some time. " +
                    "Since I want to give you credit for all the steps you do, " +
                    "please try to have your watch sync with the phone before our evening checkin. " +
                    "Can you try to do that?"
            ),
            options=['Definitely', 'Alright', "I'll try"],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )

    first_meeting = DirectedGraph(
        name='first meeting',
        start_node='ask name',
        nodes=[
            Node(
                name='ask name',
                message=Options.Messages.set_name,
                options='Okay',
                transitions='introduce self',
            ),
            Node(
                name='introduce self',
                message=Messages.introduce_self,
                options=['Nice to meet you', 'Sounds great', 'Okay'],
                transitions='can explain?'
            ),
            Node(
                name='can explain?',
                content="Can I explain how we'll work together?",
                message_type=Message.Type.MULTIPLE_CHOICE,
                options=['Sure thing', 'Okay', 'No thanks'],
                transitions=['explain checkins', 'explain checkins', 'set am checkin'],
                text_populator=text_populator,
            ),
            Node(
                name='explain checkins',
                message=Messages.explain_checkin,
                transitions='explain off-checkins',
            ),
            Node(
                name='explain off-checkins',
                message=Messages.explain_off_checkin,
                transitions='explain fitbit',
            ),
            Node(
                name='explain fitbit',
                message=Messages.explain_fitbit,
                transitions='set am checkin',
            ),
            Node(
                name='set am checkin',
                message=Options.Messages.set_am_checkin,
                transitions='confirm am checkin',
            ),
            Node(
                name='confirm am checkin',
                message=Options.Messages.confirm_am_checkin,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['set pm checkin', 'set am checkin'],
            ),
            Node(
                name='set pm checkin',
                message=Options.Messages.set_pm_checkin,
                transitions='confirm pm checkin',
            ),
            Node(
                name='confirm pm checkin',
                message=Options.Messages.confirm_pm_checkin,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['set steps goal', 'set pm checkin'],
            ),
            # THIS NODE IS SKIPPED
            Node(
                name='set day off',
                message=Options.Messages.set_day_off,
                transitions='set steps goal',
            ),
            Node(
                name='confirm day off',
                message=Options.Messages.confirm_day_off,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['set steps goal', 'set day off'],
            ),
            # ---------------------
            Node(
                name='set steps goal',
                content=(
                    lambda:
                    "The last thing to do is to set walking goals for today. " +
                    "You did {'db': '%s'} steps last week. " % state_db.Keys.STEPS_LAST_WEEK +
                    "To work towards the goal of %s steps in %s weeks, " % (
                        param_db.get(param_db.Keys.FINAL_STEPS_GOAL),
                        param_db.get(param_db.Keys.WEEKS_WITH_ROBOT)
                    ) +
                    "I suggest that you do {'db': '%s'} steps today. " % state_db.Keys.SUGGESTED_STEPS_TODAY +
                    "How many steps would you like to do today?"
                ),
                options='steps',
                message_type=Message.Type.SLIDER,
                args=[
                    lambda: "{'db': '%s'}" % state_db.Keys.MIN_SUGGESTED_STEPS_TODAY,
                    lambda: "{'db': '%s'}" % state_db.Keys.MAX_SUGGESTED_STEPS_TODAY,
                    '1',
                    lambda: "{'db': '%s'}" % state_db.Keys.SUGGESTED_STEPS_TODAY,
                ],
                result_convert_from_str_fn=int,
                result_db_key=state_db.Keys.STEPS_GOAL,
                tests=lambda x: x >= state_db.get(state_db.Keys.MIN_SUGGESTED_STEPS_TODAY),
                error_message="Please select a goal that is at least {'db': '%s'} steps" % state_db.Keys.MIN_SUGGESTED_STEPS_TODAY,
                text_populator=text_populator,
                transitions='set when walk',
            ),
            Node(
                name='set when walk',
                message=Message(
                    content="{when_question}",
                    options='is when',
                    message_type=Message.Type.TIME_ENTRY,
                    args=[
                        '15',
                        lambda: (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M"),
                    ],
                    result_db_key=state_db.Keys.WALK_TIME,
                    result_convert_from_str_fn=lambda x: datetime.datetime.strptime(x, '%I:%M %p').time(),
                    tests=lambda x: (
                            state_db.get(state_db.Keys.AM_CHECKIN_TIME) <= x <= state_db.get(state_db.Keys.PM_CHECKIN_TIME)
                    ),
                    error_message="Please pick a time after now and before our evening checkin",
                    text_populator=text_populator,
                ),
                transitions=['first closing'],
            ),
            Node(
                name='first closing',
                content=(
                    "Alright, we're all setup! " +
                    "I'll see you for checkin this evening!"
                ),
                message_type=Message.Type.MULTIPLE_CHOICE,
                options=['Bye', 'Talk to you later'],
                transitions='exit'
            )
        ],
    )

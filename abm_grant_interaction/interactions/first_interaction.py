from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator
from robotpt_common_utils import math_tools

import datetime


class Options:

    class Messages:
        ask_name = Message(
            content="What's your name?",
            options='Okay',
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.USER_NAME,
            result_type=str,
            tests=lambda x: len(x) > 1,
            error_message='Enter something with at least two letters',
            is_confirm=True,
            text_populator=text_populator,
        )
        set_am_checkin = Message(
            content="When would you like to checkin in the morning?",
            options='is when',
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.AM_CHECKIN_TIME,
            result_type=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=lambda x: x.hour < 12,
            is_confirm=True,
            text_populator=text_populator,
        )
        set_pm_checkin = Message(
            content="When should we checkin in the evening?",
            options='is when',
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.AM_CHECKIN_TIME,
            result_type=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=lambda x: x.hour >= 12,
            is_confirm=True,
            text_populator=text_populator,
        )
        set_day_off = Message(
            content="Would you like a day off",
            options=['No', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_db_key=state_db.Keys.DAY_OFF,
            text_populator=text_populator,
        )


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
                    "Can I tell you how we'll work together?"
            ),
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
            options=['Sure thing!', 'Sure', 'No thanks'],
        )
        explain_checkin = Message(
            content=(
                    "To help you walk regularly, we'll talk at least twice a day: " +
                    "once in the morning and once in the evening. " +
                    "In the morning, we'll set a walking goal for the day and I'll ask you some questions." +
                    "These questions will be about your plans to walk or about you." +
                    "In the evening, we'll review the day. If you don't meet your walking goal, I may ask you why. "
            ),
            options='Sounds good',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        explain_off_checkin = Message(
            content=(
                "You can also talk to me any other time. " +
                "I'll be happy to see you. *nod* I can tell you jokes or tell you good things." +
                "You can ask me to introduce myself, if you'd like me to meet someone new. " +
                "I can also explain how we'll work together again. " +
                "Lastly, you can change what I call you or when we have our morning and evening checkins. "
            ),
            options='Okay',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        explain_fitbit = Message(
            content=(
                    "Now I'll tell you about how I'll work with your Fitbit watch. " +
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
        ask_for_help = Message(
            content="We're setup! Is anything unclear?  Maybe I get get my *nod*human can give us a helping hand.",
            message_type=Message.Type.MULTIPLE_CHOICE,
            options='All set',
            text_populator=text_populator,
        )

    first_questions = DirectedGraph(
        name='first meeting',
        start_node='ask name',
        nodes=[
            Node(
                name='ask name',
                message=Options.Messages.ask_name,
                options='Okay',
                transitions='introduce self'
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
                transitions='set pm checkin'
            ),
            Node(
                name='set pm checkin',
                message=Options.Messages.set_pm_checkin,
                transitions='set day off'
            ),
            Node(
                name='set day off',
                message=Options.Messages.set_day_off,
                transitions='set steps goal'
            ),
            Node(
                name='set steps goal',
                content=(
                        "The last thing to do is to set your steps goal for today. " +
                        "You did {'db': '%s'} steps last week. " % state_db.Keys.STEPS_LAST_WEEK +
                        "To work towards your goal of %s steps in %s weeks, " % (
                            param_db.get(param_db.Keys.FINAL_STEPS_GOAL),
                            param_db.get(param_db.Keys.WEEKS_WITH_ROBOT)
                        ) +
                        "I suggest that you do {'db': '%s'} steps today. " % state_db.Keys.SUGGESTED_STEPS_TODAY +
                        "How many steps would you like to do today?"
                ),
                options='steps',
                message_type=Message.Type.DIRECT_INPUT,
                result_type=int,
                result_db_key=state_db.Keys.STEPS_GOAL_RECORD,
                tests=lambda x: x >= param_db.get(param_db.Keys.MIN_WEEKLY_STEPS_GOAL)/6,
                is_append_result=True,
                text_populator=text_populator,
                transitions='ask help',
    ),
            Node(
                name='ask help',
                message=Messages.ask_for_help,
                transitions='first closing',
            ),
            Node(
                name='first closing',
                content=(
                    "Whew! *shake_head*That's all. " +
                    "For any other questions, the humans should know better than me."
                ),
                message_type=Message.Type.MULTIPLE_CHOICE,
                options=['Bye', 'Talk to you later'],
                transitions='exit'
            )
        ],
    )


if __name__ == '__main__':

    from interaction_engine import InteractionEngine
    from interaction_engine.planner import MessagerPlanner
    from interaction_engine.interfaces import TerminalInterface
    from abm_grant_interaction.goal_setter.goal_calculator import GoalCalculator

    graphs_ = [
        FirstMeeting.first_questions
    ]

    # Create a plan
    plan_ = MessagerPlanner(graphs_)
    plan_.insert(FirstMeeting.first_questions)

    steps_last_week = 3000
    goal_calc = GoalCalculator()
    week_goal = goal_calc.get_week_goal(steps_last_week=steps_last_week, weeks_remaining=6)
    day_goal = goal_calc.get_day_goal(week_goal, 0, 7)

    state_db.set(state_db.Keys.STEPS_LAST_WEEK, steps_last_week)
    state_db.set(state_db.Keys.SUGGESTED_STEPS_TODAY, day_goal)

    ie = InteractionEngine(TerminalInterface(state_db), plan_, graphs_)
    ie.run()

    print(state_db)
    print(param_db)

from interaction_engine.messager import Message, DirectedGraph, Node
from abm_grant_interaction import state_db, text_populator
import datetime


class Options:

    class Messages:
        set_name = Message(
            content="What's your name?",
            options='Okay',
            args=['Your name'],
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.USER_NAME,
            result_convert_from_str_fn=str,
            tests=lambda x: len(x) > 1,
            error_message='Enter something with at least two letters',
            text_populator=text_populator,
        )
        confirm_name = Message(
            content="{transitional_statement} I'll call you {'db': '%s'} then." % state_db.Keys.USER_NAME,
            options='Okay',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        set_am_checkin = Message(
            content="When would you like to checkin in the morning?",
            options='Okay',
            message_type=Message.Type.TIME_ENTRY,
            args=['15', '8:30'],
            result_db_key=state_db.Keys.AM_CHECKIN_TIME,
            result_convert_from_str_fn=lambda x: datetime.datetime.strptime(x, '%I:%M %p').time(),
            tests=lambda x: x.hour < 12,
            error_message="Please pick a time in the morning",
            is_confirm=False,
            text_populator=text_populator,
        )
        confirm_am_checkin = Message(
            content="{transitional_statement} See you for our morning checkin at {'db': '%s'} then." % state_db.Keys.AM_CHECKIN_TIME,
            options='Okay',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        set_pm_checkin = Message(
            content="When should we checkin in the evening?",
            options='Okay',
            message_type=Message.Type.TIME_ENTRY,
            args=['15', '16:00'],
            result_db_key=state_db.Keys.PM_CHECKIN_TIME,
            result_convert_from_str_fn=lambda x: datetime.datetime.strptime(x, '%I:%M %p').time(),
            tests=lambda x: x.hour >= 12,
            error_message="Please pick a time after noon",
            is_confirm=False,
            text_populator=text_populator,
        )
        confirm_pm_checkin = Message(
            content="{transitional_statement} I'll see you for our evening checkin at {'db': '%s'} then." % state_db.Keys.PM_CHECKIN_TIME,
            options='Okay',
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        set_day_off = Message(
            content="Would you like a day off",
            options=['No', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_db_key=state_db.Keys.DAY_OFF,
            text_populator=text_populator,
        )
        confirm_day_off = Message(
            content="{transitional_statement} I'll remember that your day off is {'db': '%s'}!" % state_db.Keys.DAY_OFF,
            options="Okay",
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )

    options = DirectedGraph(
        'options',
        start_node='menu',
        nodes=[
            Node(
                name='menu',
                content='What would you like to change?',
                message_type=Message.Type.MULTIPLE_CHOICE,
                options=[
                    'What you call me',
                    'AM checkin time',
                    'PM checkin time',
                    'Nothing'
                ],
                transitions=[
                    'set name',
                    'set am checkin',
                    'set pm checkin',
                    'exit'
                ]
            ),
            Node(
                name='set name',
                message=Messages.set_name,
                transitions='confirm name',
            ),
            Node(
                name='confirm name',
                message=Messages.confirm_name,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['menu', 'set name'],
            ),
            Node(
                name='set am checkin',
                message=Messages.set_am_checkin,
                transitions='confirm am checkin',
            ),
            Node(
                name='confirm am checkin',
                message=Messages.confirm_am_checkin,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['menu', 'set am checkin'],
            ),
            Node(
                name='set pm checkin',
                message=Messages.set_pm_checkin,
                transitions='confirm pm checkin',
            ),
            Node(
                name='confirm pm checkin',
                message=Messages.confirm_pm_checkin,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['menu', 'set pm checkin'],
            ),
            Node(
                name='set day off',
                message=Messages.set_day_off,
                transitions='confirm day off',
            ),
            Node(
                name='confirm day off',
                message=Messages.confirm_day_off,
                options=['{affirmative_button_response}', '{oops_button_response}'],
                transitions=['menu', 'set day off'],
            ),
        ],
    )

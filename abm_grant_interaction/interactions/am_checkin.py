from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class Common:

    class Nodes:
        pass

    class Graphs:
        pass


class AmCheckin:

    class Nodes:
        pass

    class Graphs:
        pass

    greeting = DirectedGraph(
        name='greeting',
        nodes=[
            Node(
                name='greeting',
                content="{'var': 'greeting'}",
                options="{'var': 'greeting'}",
                message_type=Message.Type.MULTIPLE_CHOICE,
                result_type=str,
                text_populator=text_populator,
                transitions='exit'
            ),
        ],
        start_node='greeting'
    )
    basic_questions = DirectedGraph(
        name='intro',
        nodes=[
            Node(
                name='ask name',
                content="What's your name?",
                options='Okay',
                message_type=Message.Type.DIRECT_INPUT,
                result_db_key='user_name',
                result_type=str,
                tests=lambda x: len(x) > 1,
                error_message='Enter something with at least two letters',
                is_confirm=True,
                text_populator=text_populator,
                transitions='ask age'
            ),
            Node(
                name='ask age',
                content="Alright, {'db': '%s'}, how old are you?" % state_db.Keys.USER_NAME,
                options='years_old',
                message_type='direct input',
                result_type=float,
                result_db_key='user_age',
                tests=[
                    lambda x: x >= 0,
                    lambda x: x <= 200,
                ],
                error_message='Enter a number between 0 and 200',
                text_populator=text_populator,
                transitions='how are they'
            ),
            Node(
                name='how are they',
                content='How are you?',
                options=['Good', 'Okay', 'Bad'],
                message_type=Message.Type.MULTIPLE_CHOICE,
                text_populator=text_populator,
                transitions=['exit'],
            ),
        ],
        start_node='ask name'
    )
    psych_question = DirectedGraph(
        name='questions',
        nodes=[
            Node(
                name='psych question',
                content=(
                        "How do you feel about the following statement? " +
                        "'{'var': 'question', 'index': " +
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
                transitions='exit',
            ),
        ],
        start_node='psych question'
    )
    closing = DirectedGraph(
        name='closing',
        nodes=[
            Node(
                name='closing',
                content="Bye",
                options=['Bye', 'See ya!'],
                message_type=Message.Type.MULTIPLE_CHOICE,
                result_type=str,
                text_populator=text_populator,
                transitions='exit'
            ),
        ],
        start_node='closing'
    )


if __name__ == '__main__':

    from interaction_engine import InteractionEngine
    from interaction_engine.planner import MessagerPlanner
    from interaction_engine.interfaces import TerminalInterface

    graphs_ = [AmCheckin.greeting, AmCheckin.basic_questions, AmCheckin.psych_question, AmCheckin.closing]

    # Create a plan
    plan_ = MessagerPlanner(graphs_)
    plan_.insert(AmCheckin.greeting)
    plan_.insert(AmCheckin.basic_questions)
    for _ in range(3):
        plan_.insert(AmCheckin.psych_question)
    plan_.insert(AmCheckin.closing)

    ie = InteractionEngine(TerminalInterface(state_db), plan_, graphs_)
    ie.run()

    print(state_db)
    print(param_db)

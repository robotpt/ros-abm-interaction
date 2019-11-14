from abm_grant_interaction.interactions.am_checkin import AmCheckin
from abm_grant_interaction.interactions.pm_checkin import PmCheckin
from abm_grant_interaction.interactions.common import Common
from abm_grant_interaction.interactions.first_meeting import FirstMeeting
from abm_grant_interaction.interactions.off_checkin import OffCheckin
from abm_grant_interaction.interactions.options import Options

common_plans = [
    Common.Messages.greeting,
    Common.Messages.closing,
    Common.Messages.missed_checkin,
]
am_checkin_plans = [
    AmCheckin.Messages.big_5_question,
    AmCheckin.Messages.when_question,
    AmCheckin.Messages.set_goal,
    AmCheckin.where_graph,
    AmCheckin.how_motivated_graph,
    AmCheckin.how_remember_graph,
    AmCheckin.how_busy_graph,
]
pm_checkin_plans = [
    PmCheckin.Messages.no_sync,
    PmCheckin.fail_graph,
    PmCheckin.success_graph,
]
first_meeting_plans = [
    FirstMeeting.first_meeting,
]
off_checkin_plans = [
    OffCheckin.Messages.give_status,
]
option_plans = [
    Options.options,
]
possible_plans = [
    *common_plans,
    *am_checkin_plans,
    *pm_checkin_plans,
    *first_meeting_plans,
    *off_checkin_plans,
    *option_plans,
]

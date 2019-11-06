import datetime
import math

from robotpt_common_utils import dates, math_tools


class SessionPlanner:

    def __init__(
            self,
            start_date=None,
            days_in_session=7,
    ):
        if start_date is None:
            start_date = datetime.date.today()

        self._start_date = start_date
        self._days_in_session = days_in_session

    def get_days_since_start_date(self, date=None):
        if date is None:
            date = datetime.date.today()
        if date < self._start_date:
            raise ValueError("Date must not be before the start date")
        return (date - self._start_date).days

    def get_session_num(self, date=None):
        days_delta = self.get_days_since_start_date(date)
        return math.floor(days_delta/self._days_in_session)

    def get_day_in_current_session(self, date=None):
        days_delta = self.get_days_since_start_date(date)
        return days_delta % self._days_in_session

    def get_days_left_in_current_session(self, date=None):
        day_in_session = self.get_day_in_current_session(date)
        return self._days_in_session - day_in_session

    def get_first_day_in_current_session(self, date=None):
        session_num = self.get_session_num(date)
        return self.get_first_day_of_session(session_num)

    def get_first_day_of_session(self, session_num):
        if session_num < 0:
            raise ValueError("'session_num' must not be negative")
        return self._start_date + datetime.timedelta(
            days=session_num*self._days_in_session
        )

    def get_last_day_in_current_session(self, date=None):
        session_num = self.get_session_num(date)
        return self.get_last_day_of_session(session_num)

    def get_last_day_of_session(self, session_num):
        return self._start_date + datetime.timedelta(
            days=(session_num+1)*self._days_in_session-1
        )

    def get_current_session_date_range(self, date=None, output_format=None):
        session_num = self.get_session_num(date)
        return self.get_session_date_range(session_num, output_format)

    def get_session_date_range(self, session_num, output_format=None):

        if not math_tools.is_int(session_num) and session_num < 0:
            raise ValueError("'session_num' must be a non-negative int")

        first_day = self.get_first_day_of_session(session_num)
        last_day = self.get_last_day_of_session(session_num)
        return dates.get_date_range(
            start_date=first_day,
            end_date=last_day + datetime.timedelta(days=1),
            increment_days=1,
            output_format=output_format,
        )

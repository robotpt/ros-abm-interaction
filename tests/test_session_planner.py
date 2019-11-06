import unittest
import datetime

from abm_grant_interaction.goal_setter import SessionPlanner


class TestSessionPlanner(unittest.TestCase):

    def test_exception_on_date_before_session(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )

        for i in range(1, 10):
            timedelta = datetime.timedelta(days=i)
            self.assertRaises(
                ValueError,
                s.get_days_since_start_date,
                start_date - timedelta
            )

    def test_get_day_in_current_session(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )
        for j in range(10):
            for i in range(days_in_session):
                timedelta = datetime.timedelta(
                    days=days_in_session*j+i)
                self.assertEqual(
                    i,
                    s.get_day_in_current_session(date=start_date + timedelta)
                )

    def test_get_days_left_in_current_session(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )
        days_left = s.get_days_left_in_current_session(start_date+datetime.timedelta(days=3))
        self.assertEqual(
            10,
            days_left
        )

    def test_get_session_num(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )
        for j in range(10):
            for i in range(days_in_session):
                timedelta = datetime.timedelta(
                    days=days_in_session*j+i)
                self.assertEqual(
                    j,
                    s.get_session_num(date=start_date + timedelta)
                )

    def test_get_first_day_of_current_session(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )
        for j in range(10):
            first_day_of_session = start_date + datetime.timedelta(days=days_in_session*j)
            for i in range(days_in_session):
                timedelta = datetime.timedelta(
                    days=days_in_session*j+i)
                self.assertEqual(
                    first_day_of_session,
                    s.get_first_day_in_current_session(date=start_date + timedelta)
                )

    def test_get_last_day_of_current_session(self):

        start_date = datetime.date(2019, 10, 1)
        days_in_session = 13
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )
        for j in range(10):
            last_day_of_session = start_date + datetime.timedelta(days=days_in_session*(j+1)-1)
            for i in range(days_in_session):
                timedelta = datetime.timedelta(
                    days=days_in_session*j+i)
                self.assertEqual(
                    last_day_of_session,
                    s.get_last_day_in_current_session(date=start_date + timedelta)
                )

    def test_get_session_date_range(self):
        start_date = datetime.date(2019, 10, 1)
        days_in_session = 3
        s = SessionPlanner(
            start_date=start_date,
            days_in_session=days_in_session,
        )

        date = start_date + datetime.timedelta(days=days_in_session*2)
        truth_date_range = [
            '2019-10-07',
            '2019-10-08',
            '2019-10-09',
        ]
        test_date_range = s.get_current_session_date_range(date, output_format='%Y-%m-%d')

        self.assertEqual(
            len(truth_date_range),
            len(test_date_range)
        )
        for i in range(len(truth_date_range)):
            self.assertEqual(
                truth_date_range[i],
                test_date_range[i]
            )

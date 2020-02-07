import datetime
import pandas
import statistics

from fitbit_client import FitbitClient
from robotpt_common_utils import pandas_lib


class AbmFitbitClient:

    class FitbitApi:
        API_URL = "api.fitbit.com"
        STEPS_RESOURCE_PATH = "activities/steps"
        STEPS_DETAIL_LEVEL_1_MIN = "1min"
        LAST_SYNC_KEY = "lastSyncTime"

    class StepsDataframe:
        STEPS_COLUMN = "Steps"
        TIME_COLUMN = "Time"

    def __init__(
            self,
            credentials_file_path: str = "fitbit_credentials.yaml",
            redirect_url: str = "http://localhost",
            min_steps_for_entry_to_be_active: int = 20,
            max_contiguous_non_active_entries_for_continuous_session: int = 3,
            min_consecutive_active_entries_to_count_as_activity: int = 10,
    ):
        self._fitbit = FitbitClient(
            credentials_file_path=credentials_file_path,
            redirect_url=redirect_url,
        )

        self._min_active_steps = min_steps_for_entry_to_be_active
        self._max_inactive_minutes_before_stop = max_contiguous_non_active_entries_for_continuous_session
        self._min_activity_duration = min_consecutive_active_entries_to_count_as_activity

    def get_last_sync(self):
        url = "https://{api_url}/1/user/-/devices.json".format(
            api_url=self.FitbitApi.API_URL,
        )
        response = self._fitbit.request_url(url)
        data_idx = 0
        last_sync_str = response[data_idx][self.FitbitApi.LAST_SYNC_KEY]+"000"  # zeros pad microseconds for parsing
        str_format = "%Y-%m-%dT%H:%M:%S.%f"
        return datetime.datetime.strptime(last_sync_str, str_format)

    def get_active_steps_features(self, date: datetime.date = None):
        active_dataframes = self._get_active_dataframes(date)
        if active_dataframes is None:
            return None

        steps_per_walk = [df[AbmFitbitClient.StepsDataframe.STEPS_COLUMN].sum() for df in active_dataframes]
        minutes_per_walk = [len(df) for df in active_dataframes]

        active_steps = pandas.concat(active_dataframes)
        steps_column = active_steps[AbmFitbitClient.StepsDataframe.STEPS_COLUMN]

        return {
            'mean steps per walk': statistics.mean(steps_per_walk),
            'median steps per walk': statistics.median(steps_per_walk),
            'max steps per walk': max(steps_per_walk),
            'min steps per walk': min(steps_per_walk),

            'mean minutes per walk': statistics.mean(minutes_per_walk),
            'median minutes per walk': statistics.median(minutes_per_walk),
            'max minutes walked': max(minutes_per_walk),
            'min minutes walked': min(minutes_per_walk),

            'mean steps per minute': steps_column.mean(),
            'median steps per minute': steps_column.median(),
            'max steps per minute': steps_column.max(),
            'min steps per minute': steps_column.min(),

            'total steps': steps_column.sum(),
            'total minutes walked': sum(minutes_per_walk),
        }

    def _get_active_dataframe(self, date: datetime.date = None):

        active_dataframes = self._get_active_dataframes(date)
        if active_dataframes is None:
            return None

        return pandas.concat(active_dataframes)

    def _get_active_dataframes(self, date: datetime.date = None):

        all_steps = self.get_intraday_steps(date)

        active_steps_with_inactive_as_nan = all_steps.where(
            all_steps[self.StepsDataframe.STEPS_COLUMN] >= self._min_active_steps
        )
        consecutive_active_steps_separated_with_nan = pandas_lib.remove_consecutive_nans(
            active_steps_with_inactive_as_nan,
            self.StepsDataframe.STEPS_COLUMN,
            self._max_inactive_minutes_before_stop,
        )
        active_dataframes_of_any_length = pandas_lib.split_on_nan(consecutive_active_steps_separated_with_nan, self.StepsDataframe.STEPS_COLUMN)

        active_dataframes_with_min_duration = [
            df
            for df in active_dataframes_of_any_length
            if len(df) >= self._min_activity_duration
        ]

        if active_dataframes_with_min_duration:
            return active_dataframes_with_min_duration
        else:
            return None

    def get_intraday_steps(self, date: datetime.date = None):
        url = "https://{api_url}/1/user/-/{resource_path}/date/{date}/1d/{detail_level}.json".format(
            api_url=self.FitbitApi.API_URL,
            resource_path=self.FitbitApi.STEPS_RESOURCE_PATH,
            date=self._date_to_fitbit_date_string(date),
            detail_level=self.FitbitApi.STEPS_DETAIL_LEVEL_1_MIN,
        )
        response = self._fitbit.request_url(url)
        return self._fitbit_steps_response_to_dataframe(response)

    @staticmethod
    def _fitbit_steps_response_to_dataframe(response):
        times = []
        steps = []
        for i in response['activities-steps-intraday']['dataset']:
            steps.append(i['value'])
            times.append(i['time'])
        return pandas.DataFrame(
            {
                AbmFitbitClient.StepsDataframe.TIME_COLUMN: times,
                AbmFitbitClient.StepsDataframe.STEPS_COLUMN: steps,
            }
        )

    @staticmethod
    def _date_to_fitbit_date_string(date: datetime.date = None):

        if date is None:
            return "today"

        return date.strftime('%Y-%m-%d')


if __name__ == '__main__':

    credentials_path = "/root/ws/catkin_ws/src/abm_interaction/src/fitbit-client/fitbit_client/fitbit_credentials.yaml"
    fc = AbmFitbitClient(credentials_path)
    out = fc.get_last_sync()
    print(out)

    date = out.date()
    out = fc.get_intraday_steps(date)
    print(out)

    out = fc._get_active_dataframes(date)
    print(out)

    out = fc.get_active_steps_features(date)
    print(out)

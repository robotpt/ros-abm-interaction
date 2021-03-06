#!/usr/bin/env python3.6

import datetime
import pandas
import statistics
import logging

from fitbit_client import FitbitClient
from robotpt_common_utils import pandas_lib


class WalkFeatures:
    MEAN_STEPS_PER_WALK = 'mean_steps_per_walk'
    MEDIAN_STEPS_PER_WALK = 'median_steps_per_walk'
    MAX_STEPS_PER_WALK = 'max_steps_per_walk'
    MIN_STEPS_PER_WALK = 'min_steps_per_walk'

    MEAN_MINUTES_PER_WALK = 'mean_minutes_per_walk'
    MEDIAN_MINUTES_PER_WALK = 'median_minutes_per_walk'
    MAX_MINUTES_WALKED = 'max_minutes_walked'
    MIN_MINUTES_WALKED = 'min_minutes_walked'

    MEAN_STEPS_PER_MINUTE = 'mean_steps_per_minute'
    MEDIAN_STEPS_PER_MINUTE = 'median_steps_per_minute'
    MAX_STEPS_PER_MINUTE = 'max_steps_per_minute'
    MIN_STEPS_PER_MINUTE = 'min_steps_per_minute'

    TOTAL_STEPS = 'total_steps'
    TOTAL_MINUTES_WALKED = 'total_minutes_walked'

    DURATION_FOR_EACH_WALK = 'duration_for_each_walk'
    STEPS_EACH_WALK = 'steps_each_walk'


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

        self._active_steps_cache = dict()
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

    def get_total_steps(self, date: datetime.date = None):
        return self._get_feature(
            WalkFeatures.TOTAL_STEPS,
            date,
            0
        )

    def get_steps_per_minute(self, date: datetime.date = None):
        return self._get_feature(
            WalkFeatures.MEAN_STEPS_PER_MINUTE,
            date,
            0.0,
        )

    def get_durations_for_each_walk(self, date: datetime.date = None):
        return self._get_feature(
            WalkFeatures.DURATION_FOR_EACH_WALK,
            date,
            none_return=[],
        )

    def get_steps_for_each_walk(self, date: datetime.date = None):
        return self._get_feature(
            WalkFeatures.STEPS_EACH_WALK,
            date,
            none_return=[],
        )

    def _get_feature(self, feature, date: datetime.date = None, none_return: any = 0):
        features = self.get_features_of_active_steps(date)
        if features is None:
            return none_return
        else:
            return features[feature]

    def get_features_of_active_steps(
            self,
            date: datetime.date = None,
    ):

        if date in self._active_steps_cache.keys():
            logging.info("Steps data read from cache")
            return self._active_steps_cache[date]

        logging.info("Requesting steps info from Fitbit")
        features = self._get_features_of_active_steps(date)
        # Don't cache steps for the day until it's over
        if date != datetime.datetime.now().date():
            logging.info("Steps data saved in the cache")
            self._active_steps_cache[date] = features
        return features

    def _get_features_of_active_steps(self, date: datetime.date = None):
        active_dataframes = self._get_active_dataframes(date)
        if active_dataframes is None:
            return None

        steps_per_walk = [int(df[AbmFitbitClient.StepsDataframe.STEPS_COLUMN].sum()) for df in active_dataframes]
        minutes_per_walk = [len(df) for df in active_dataframes]

        active_steps = pandas.concat(active_dataframes)
        steps_column = active_steps[AbmFitbitClient.StepsDataframe.STEPS_COLUMN]

        return {
            WalkFeatures.MEAN_STEPS_PER_WALK: statistics.mean(steps_per_walk),
            WalkFeatures.MEDIAN_STEPS_PER_WALK: statistics.median(steps_per_walk),
            WalkFeatures.MAX_STEPS_PER_WALK: max(steps_per_walk),
            WalkFeatures.MIN_STEPS_PER_WALK: min(steps_per_walk),

            WalkFeatures.MEAN_MINUTES_PER_WALK: statistics.mean(minutes_per_walk),
            WalkFeatures.MEDIAN_MINUTES_PER_WALK: statistics.median(minutes_per_walk),
            WalkFeatures.MAX_MINUTES_WALKED: max(minutes_per_walk),
            WalkFeatures.MIN_MINUTES_WALKED: min(minutes_per_walk),

            WalkFeatures.MEAN_STEPS_PER_MINUTE: steps_column.mean(),
            WalkFeatures.MEDIAN_STEPS_PER_MINUTE: steps_column.median(),
            WalkFeatures.MAX_STEPS_PER_MINUTE: steps_column.max(),
            WalkFeatures.MIN_STEPS_PER_MINUTE: steps_column.min(),

            WalkFeatures.TOTAL_STEPS: int(steps_column.sum()),
            WalkFeatures.TOTAL_MINUTES_WALKED: int(sum(minutes_per_walk)),

            WalkFeatures.DURATION_FOR_EACH_WALK: minutes_per_walk,
            WalkFeatures.STEPS_EACH_WALK: steps_per_walk,
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
        active_dataframes_of_any_length = pandas_lib.split_on_nan(
            consecutive_active_steps_separated_with_nan,
            self.StepsDataframe.STEPS_COLUMN,
        )

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

    fc = AbmFitbitClient()
    out = fc.get_last_sync()
    print(out)

    date_ = out.date()
    out = fc.get_intraday_steps(date_)
    print(out)

    out = fc.get_total_steps(date_)
    print(out)

    out = fc.get_steps_for_each_walk(date_)
    print(out)

    out = fc.get_durations_for_each_walk()
    print(out)

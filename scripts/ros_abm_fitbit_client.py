#!/usr/bin/env python3.6

from abm_fitbit_client import AbmFitbitClient, WalkFeatures

import rospy
import datetime

from abm_interaction.srv import ActiveStepsOnDate, ActiveStepsOnDateResponse


class RosAbmFitbitClient:

    def __init__(
            self,
            active_steps_on_date_topic,
            credentials_file_path,
            redirect_url,
    ):

        self._active_steps_cache = dict()
        self._fitbit = AbmFitbitClient(
            credentials_file_path=credentials_file_path,
            redirect_url=redirect_url,
        )

        rospy.init_node("fitbit_client")
        rospy.Service(
            active_steps_on_date_topic,
            ActiveStepsOnDate,
            self._get_active_steps_callback,
        )

    def _get_active_steps_callback(self, request):

        rospy.loginfo("Active steps requested for {y}-{m}-{d}".format(
            y=request.year,
            m=request.month,
            d=request.day,
        ))

        try:
            date = datetime.date(request.year, request.month, request.day)
        except ValueError as e:
            raise ValueError("Must be valid date request") from e

        response = ActiveStepsOnDateResponse()
        try:
            data = self.get_active_steps(date)
            if data is not None:
                response.total_steps = data[WalkFeatures.TOTAL_STEPS]
                response.steps_per_minute = data[WalkFeatures.MEAN_STEPS_PER_MINUTE]
                response.walk_steps = data[WalkFeatures.STEPS_EACH_WALK]
                response.walk_durations = data[WalkFeatures.DURATION_FOR_EACH_WALK]
        except Exception as e:
            raise Exception from e
        return response

    def get_active_steps(
            self,
            date: datetime.date = None,
    ):

        if date in self._active_steps_cache.keys():
            rospy.loginfo("Steps read from cache")
            return self._active_steps_cache[date]

        features = self._fitbit.get_features_of_active_steps(date)
        # Don't cache steps for the day until it's over
        if date != datetime.datetime.now().date():
            rospy.loginfo("Steps for the day saved in the cache")
            self._active_steps_cache[date] = features
        return features


if __name__ == '__main__':

    client = RosAbmFitbitClient(
        active_steps_on_date_topic=rospy.get_param(
            "abm/fitbit/active_steps_topic",
            default="abm/fitbit/get_active_steps",
        ),
        credentials_file_path=rospy.get_param(
            "abm/fitbit/oauth2/credentials_file_path",
            default="fitbit_credentials.yaml",
        ),
        redirect_url=rospy.get_param(
            "abm/fitbit/oauth2/redirect_url",
            default="http://localhost",
        ),
    )

    rospy.spin()

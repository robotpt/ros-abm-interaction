#!/usr/bin/env python3.6

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup
import os

package_dirs = {
    'abm_grant_interaction': os.path.join('src', 'abm-grant-interaction', 'abm_grant_interaction'),
    'abm_fitbit_client': os.path.join('src', 'abm_fitbit_client'),
    'fitbit_client': os.path.join('src', 'fitbit-client', 'fitbit_client'),
    'interaction_engine': os.path.join('src', 'interaction-engine', 'interaction_engine'),
    'pickled_database': os.path.join('src', 'pickle-database', 'pickled_database'),
    'robotpt_common_utils': os.path.join('src', 'robotpt-common-utils', 'robotpt_common_utils'),
}

d = generate_distutils_setup(
    packages=package_dirs.keys(),
    package_dir=package_dirs,
)
setup(**d)

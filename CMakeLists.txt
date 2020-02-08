cmake_minimum_required(VERSION 2.8.3)
project(abm_interaction)
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  std_srvs
  message_generation
)
add_service_files(
  FILES
  ActiveStepsOnDate.srv
)
catkin_python_setup()
generate_messages(
  DEPENDENCIES
  std_msgs
)
catkin_package(
  CATKIN_DEPENDS
  message_runtime
)

# catkin_add_nosetests(test)

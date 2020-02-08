cmake_minimum_required(VERSION 2.8.3)
project(abm_interaction)
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  cordial_gui
)
catkin_python_setup()
catkin_package()

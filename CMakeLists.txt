cmake_minimum_required(VERSION 2.8.3)
project(abm_interaction)
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  std_srvs
)

catkin_python_setup()
catkin_package()

# catkin_add_nosetests(test)

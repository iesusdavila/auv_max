cmake_minimum_required(VERSION 3.8)
project(auv_max_sonar)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

include_directories(
  include
)

add_library(${PROJECT_NAME}_lib
  "src/sonar_obstacle_detector.cpp"
)

set(DEPENDENCIES
  "rclcpp"
  "sensor_msgs"
)

target_link_libraries(${PROJECT_NAME}_lib)
ament_target_dependencies(${PROJECT_NAME}_lib ${DEPENDENCIES})

set(EXEC_NAME "auv_max_sonar")

add_executable(${EXEC_NAME} src/sonar_obstacle_detector.cpp)
target_link_libraries(${EXEC_NAME} ${PROJECT_NAME}_lib ncurses)
ament_target_dependencies(${EXEC_NAME} ${DEPENDENCIES})


install(TARGETS ${EXEC_NAME}
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

ament_export_include_directories(include)
ament_export_dependencies(rclcpp)
ament_export_dependencies(sensor_msgs)
ament_package()

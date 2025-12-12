cmake_minimum_required(VERSION 3.8)
project(call)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED) # เพิ่ม rclcpp สำหรับการเขียน Node C++
find_package(std_msgs REQUIRED) # <-- ใช้ std_msgs เท่านั้น
find_package(rosidl_default_generators REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# --- สร้าง Service Interface ---
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/Setposi.srv"
  DEPENDENCIES std_msgs # ใช้ std_msgs เท่านั้น
)

# --- เพิ่ม dependencies สำหรับ Executables (ถ้ามี) ---
# ถ้าคุณจะสร้าง Node C++ ที่ใช้ Service นี้:
# ament_target_dependencies(your_node_name rclcpp std_msgs ${PROJECT_NAME}__rosidl_generator_cpp)

ament_package()
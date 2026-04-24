add_executable(SimpleExample main.cpp)
target_link_libraries(SimpleExample PRIVATE SerialComm::SerialComm)

add_executable(ClaudeExample ClaudeExample.cpp)
target_link_libraries(ClaudeExample PRIVATE SerialComm::SerialComm)
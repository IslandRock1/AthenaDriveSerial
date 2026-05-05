
#include <iostream>
#include <chrono>
#include "SerialComm/SerialComm.hpp"

int main() {
    SerialComm serialComm("COM6"); // Probably "/dev/ttyACM0" for linux.

    // Adjust the following values as wanted.
    serialComm.setNumPolePairs(7);
    serialComm.setCurrentLimit(2000);
    serialComm.setVelocityKp(1.0);
    serialComm.setPositionKp(1.0);
    serialComm.setDrivingMode(DrivingMode::Position); // For velocity, change this to "DrivingMode::Velocity"

    SensorData data;
    for (int i = 0; i < 1000; i++) {
        serialComm.getData(data);
        std::cout << data.timestamp_ms << " | Position: " << data.position << " | Current: " << data.current << std::endl;

        serialComm.setPositionSetpoint(static_cast<float>(i)); // For velocity, change this to ".setVelocitySetpoint"
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}
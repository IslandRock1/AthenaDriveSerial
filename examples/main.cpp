#include <iostream>
#include <chrono>
#include <cmath>
#include "SerialComm/SerialComm.hpp"

int main() {
    SerialComm serialComm("/dev/ttyACM0");
    std::cout << "Connected. Receiving data from ESP32...\n";

    Command cmd{CommandType::TorqueSetpoint, 0, 0.0};
    serialComm.sendData(cmd);

    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Torque;
    serialComm.sendData(cmd);

    cmd.command_type = CommandType::TorqueSetpoint;

    auto t0 = std::chrono::high_resolution_clock::now();
    auto prevSendTime = t0;
    while (1) {
        auto timeNow = std::chrono::high_resolution_clock::now();
        auto timeSinceSend = std::chrono::duration_cast<std::chrono::milliseconds>(timeNow - prevSendTime).count();
        if (timeSinceSend > 50) {
            prevSendTime = timeNow;
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(timeNow - t0).count();
            auto t = static_cast<double>(ms) / 1000.0;

            auto torque = std::sin(t) / 5.0;
            cmd.value1 = torque;
            serialComm.sendData(cmd);
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}
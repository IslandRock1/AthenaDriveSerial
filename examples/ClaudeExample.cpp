
/*

THIS EXAMPLE IS MADE BY CLAUD AI
(And slight fixes by humans)

*/

#include <iostream>
#include <chrono>
#include <cmath>
#include <thread>
#include "SerialComm/SerialComm.hpp"

int main() {
    // SerialComm serialComm("/dev/ttyACM0");  // Linux / macOS
    SerialComm serialComm("COM4");             // Windows

    std::cout << "Connected.\n";

    SensorData data;
    Command cmd{};

    // --- Configure ---
    // Set driving mode to Velocity
    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Velocity;
    serialComm.sendData(cmd);

    // Set velocity PID gains
    cmd.command_type = CommandType::VelocityKp;
    cmd.value1 = 0.05f;
    serialComm.sendData(cmd);

    cmd.command_type = CommandType::VelocityKi;
    cmd.value1 = 0.0f;
    serialComm.sendData(cmd);

    // --- Run ---
    auto t0           = std::chrono::high_resolution_clock::now();
    auto prevSendTime = t0;

    cmd.command_type = CommandType::VelocitySetpoint;

    while (true) {
        auto now          = std::chrono::high_resolution_clock::now();
        auto msSinceStart = std::chrono::duration_cast<std::chrono::milliseconds>(now - t0).count();
        auto msSinceSend  = std::chrono::duration_cast<std::chrono::milliseconds>(now - prevSendTime).count();
        double t = msSinceStart / 5000.0;

        // Send a new setpoint every 50 ms
        if (msSinceSend >= 50) {
            prevSendTime = now;
            cmd.value1 = static_cast<float>(10.0 * std::sin(t));  // ±3 rad/s sine wave
            serialComm.sendData(cmd);
            std::cout << "Sent velocity setpoint: " << cmd.value1 << " rad/s"
                      << "  (buffer: " << serialComm.getNumRemainingCommands() << ")\n";
        }

        // Read and print sensor data
        serialComm.getData(data);
        std::cout << "  pos=" << data.position << " rad"
                  << "  vel=" << data.velocity << " rad/s"
                  << "  torque=" << data.torque << " Nm"
                  << "  iter=" << data.iteration << "\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}
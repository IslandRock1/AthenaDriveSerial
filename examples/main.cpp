#include <iostream>
#include <chrono>
#include "../include/SerialComm/SerialComm.hpp"

int main() {
    SerialComm serialComm("COM3");

    std::cout << "Connected. Receiving data from ESP32...\n";
    std::cout << "(Press 's' + Enter to send a command)\n";

    Command cmd{3, 0, 1.0};
    serialComm.sendData(cmd);

    cmd.command_type = 1;
    int commandIteration = 1;

    while (true) {
        if (commandIteration++ % 100 == 0) {
            serialComm.sendData(cmd);
        }

        // Read and cache the latest packet from the ESP32
        if (serialComm.update()) {
            SensorData data;
            serialComm.getData(data);
            std::cout << "Received: iter=" << data.iteration
                      << ", time=" << data.timestamp_ms
                      << " ms, pos=" << data.position
                      << ", vel=" << data.velocity << "\n";
        }
    }
}
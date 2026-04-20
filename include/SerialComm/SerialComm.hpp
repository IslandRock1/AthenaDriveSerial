#pragma once

#include <cstdint>
#include <string>
#include <thread>
#include <mutex>
#include <atomic>
#include <queue>
#include <serial_cpp/serial.h>
#include "SerialConfig.hpp"

class SerialComm {
public:
	explicit SerialComm(const std::string &port_name,
						uint32_t baudrate      = 115200,
						uint32_t timeout_ms    = 1000);

	~SerialComm();
	void sendData(const Command &cmd);
	bool getData(SensorData &data);
	unsigned long long getNumRemainingCommands();

private:
	static constexpr uint8_t SYNC_BYTE_0 = 0xAA;
	static constexpr uint8_t SYNC_BYTE_1 = 0x55;

	void readData();
	void writeData();
	void update();
	std::mutex _incomingMutex;
	std::mutex _outgoingMutex;
	std::jthread _serialThread;
	std::atomic_bool _stopFlag = false;
	std::atomic_bool _debugPrint = false;

	serial_cpp::Serial _m_port;
	std::queue<Command> _commands;
	SensorData _m_rx_data{};
	bool _m_has_data = false;
};
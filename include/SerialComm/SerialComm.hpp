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

	// Torque control
	void setTorqueSetpoint(float value);
	void setTorqueKp(float value);
	void setTorqueKi(float value);
	void setTorqueKd(float value); // Not in use

	// Velocity control
	void setVelocitySetpoint(float value);
	void setVelocityKp(float value);
	void setVelocityKi(float value);
	void setVelocityKd(float value);

	// Position control
	void setPositionSetpoint(float value);
	void setPositionKp(float value);
	void setPositionKi(float value);
	void setPositionKd(float value);

	// System / mode
	void setDrivingMode(int32_t value);

	// Limits / configuration
	void setCurrentLimit(int32_t value);
	void setNumPolePairs(int32_t value);

	// Open loop
	void setOpenLoopSpeed(float value);
	void setOpenLoopStrength(float value);

private:
	Command _cmd;

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
#include "SerialComm/SerialComm.hpp"
#include <iostream>
#include <stdexcept>
#include <chrono>

SerialComm::SerialComm(const std::string &port_name,
					   uint32_t baudrate,
					   uint32_t timeout_ms) {
	_m_port.setPort(port_name);
	_m_port.setBaudrate(baudrate);

	auto timeOutVal = serial_cpp::Timeout::simpleTimeout(timeout_ms);
	_m_port.setTimeout(timeOutVal);
	_m_port.open();

	if (!_m_port.isOpen()) {
		throw std::runtime_error("Failed to open serial port: " + port_name);
	}

	_serialThread = std::jthread{&SerialComm::update, this};
}

SerialComm::~SerialComm() {
	_stopFlag = true;

	if (_serialThread.joinable()) {
		_serialThread.join();
	}

	if (_m_port.isOpen()) {
		_m_port.close();
	}
}

void SerialComm::sendData(const Command &cmd) {
	std::lock_guard<std::mutex> lock(_outgoingMutex);
	if (_commands.size() > 0) {
		if (_commands.back().command_type == cmd.command_type) {
			_commands.back().value1 = cmd.value1;
			_commands.back().value0 = cmd.value0;
			return;
		}
	}
	_commands.push(cmd);
}

bool SerialComm::getData(SensorData &data) {
	std::lock_guard<std::mutex> lock(_incomingMutex);
	if (!_m_has_data) return false;
	data = _m_rx_data;
	return true;
}

unsigned long long SerialComm::getNumRemainingCommands() {
	std::lock_guard<std::mutex> lock(_outgoingMutex);
	return _commands.size();
}

void SerialComm::readData() {
	static uint8_t byte;

	if (_m_port.read(&byte, 1) != 1) return;
	if (byte != SYNC_BYTE_0) return;

	if (_m_port.read(&byte, 1) != 1) return;
	if (byte != SYNC_BYTE_1) return;

	// Sync found — read the payload into the cache
	uint8_t buffer[sizeof(SensorData)];
	if (_m_port.read(buffer, sizeof(SensorData)) != sizeof(SensorData)) {
		if (_debugPrint) {
			std::cout << "Found sync bytes, but could not read complete sensordata. In SerialComm::update.\n";
		}
	} else {
		std::lock_guard<std::mutex> lock(_incomingMutex);
		std::memcpy(&_m_rx_data, buffer, sizeof(SensorData));
		_m_has_data = true;
	}
}

void SerialComm::writeData() {
	std::lock_guard<std::mutex> lock(_outgoingMutex);
	if (_commands.empty()) { return; }
	Command _cmd = _commands.front();

	size_t written = _m_port.write(
	reinterpret_cast<const uint8_t *>(&_cmd), sizeof(Command));

	if (written != sizeof(Command)) {
		std::cerr << "SerialComm: failed to send full command (sent "
				  << written << " of " << sizeof(Command) << " bytes)\n";
	} else {
		_commands.pop();
	}
}

void SerialComm::update() {
	auto prevSend = std::chrono::high_resolution_clock::now();
	while (!_stopFlag) {
		readData();

		auto timeNow = std::chrono::high_resolution_clock::now();
		auto durationSinceWrite = std::chrono::duration_cast<std::chrono::microseconds>(timeNow - prevSend).count();

		// Using 10.107ms in the hopes that it wont sync up with esp.
		// Would probably be fine.. but idk.
		if (durationSinceWrite > 10107) {
			prevSend = timeNow;
			writeData();
		}
	}
}

// Torque control
void SerialComm::setTorqueSetpoint(float value) {
    _cmd.command_type = CommandType::TorqueSetpoint;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setTorqueKp(float value) {
    _cmd.command_type = CommandType::TorqueKp;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setTorqueKi(float value) {
    _cmd.command_type = CommandType::TorqueKi;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setTorqueKd(float value) {
    _cmd.command_type = CommandType::TorqueKd;
    _cmd.value1 = value;
    sendData(_cmd);
}

// Velocity control
void SerialComm::setVelocitySetpoint(float value) {
    _cmd.command_type = CommandType::VelocitySetpoint;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setVelocityKp(float value) {
    _cmd.command_type = CommandType::VelocityKp;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setVelocityKi(float value) {
    _cmd.command_type = CommandType::VelocityKi;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setVelocityKd(float value) {
    _cmd.command_type = CommandType::VelocityKd;
    _cmd.value1 = value;
    sendData(_cmd);
}

// Position control
void SerialComm::setPositionSetpoint(float value) {
    _cmd.command_type = CommandType::PositionSetpoint;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setPositionKp(float value) {
    _cmd.command_type = CommandType::PositionKp;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setPositionKi(float value) {
    _cmd.command_type = CommandType::PositionKi;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setPositionKd(float value) {
    _cmd.command_type = CommandType::PositionKd;
    _cmd.value1 = value;
    sendData(_cmd);
}

// System / mode
void SerialComm::setDrivingMode(int32_t value) {
    _cmd.command_type = CommandType::DrivingModeCommand;
    _cmd.value0 = value;
    sendData(_cmd);
}

// Limits / configuration
void SerialComm::setCurrentLimit(int32_t value) {
    _cmd.command_type = CommandType::CurrentLimit;
    _cmd.value0 = value;
    sendData(_cmd);
}

void SerialComm::setNumPolePairs(int32_t value) {
    _cmd.command_type = CommandType::NumPolePairs;
    _cmd.value0 = value;
    sendData(_cmd);
}

// Open loop
void SerialComm::setOpenLoopSpeed(float value) {
    _cmd.command_type = CommandType::OpenLoopSpeed;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setOpenLoopStrength(float value) {
    _cmd.command_type = CommandType::OpenLoopStrength;
    _cmd.value1 = value;
    sendData(_cmd);
}

void SerialComm::setTorqueSign(float value) {
	_cmd.command_type = CommandType::TorqueSign;
	_cmd.value1 = value;
	sendData(_cmd);
}

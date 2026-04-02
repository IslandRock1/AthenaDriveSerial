#include "SerialComm/SerialComm.hpp"
#include <iostream>
#include <stdexcept>

SerialComm::SerialComm(const std::string &port_name,
					   uint32_t baudrate,
					   uint32_t timeout_ms) {
	m_port.setPort(port_name);
	m_port.setBaudrate(baudrate);

	auto timeOutVal = serial_cpp::Timeout::simpleTimeout(timeout_ms);
	m_port.setTimeout(timeOutVal);
	m_port.open();

	if (!m_port.isOpen()) {
		throw std::runtime_error("Failed to open serial port: " + port_name);
	}
}

SerialComm::~SerialComm() {
	if (m_port.isOpen()) {
		m_port.close();
	}
}

bool SerialComm::sendData(const Command &cmd) {
	size_t written = m_port.write(
		reinterpret_cast<const uint8_t *>(&cmd), sizeof(Command));

	if (written != sizeof(Command)) {
		std::cerr << "SerialComm: failed to send full command (sent "
				  << written << " of " << sizeof(Command) << " bytes)\n";
		return false;
	}
	return true;
}

bool SerialComm::getData(SensorData &data) const {
	if (!m_has_data) return false;
	data = m_rx_data;
	return true;
}

bool SerialComm::update() {
	uint8_t byte;

	// Scan for sync header 0xAA 0x55
	while (true) {
		if (m_port.read(&byte, 1) != 1) return false;
		if (byte != SYNC_BYTE_0) continue;

		if (m_port.read(&byte, 1) != 1) return false;
		if (byte != SYNC_BYTE_1) continue;

		// Sync found — read the payload into the cache
		uint8_t buffer[sizeof(SensorData)];
		if (m_port.read(buffer, sizeof(SensorData)) != sizeof(SensorData)) {
			return false;
		}
		std::memcpy(&m_rx_data, buffer, sizeof(SensorData));
		m_has_data = true;
		return true;
	}
}
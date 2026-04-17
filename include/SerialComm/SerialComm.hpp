#pragma once

#include <cstdint>
#include <cstring>
#include <string>
#include <serial_cpp/serial.h>

// --- Packed structures (must match ESP32 exactly) ---
#pragma pack(push, 1)
struct SensorData {
	uint32_t iteration;
	uint32_t timestampMS;
	float position;
	float velocity;
	float torque;
	float current;
};

struct Command {
	uint8_t commandType;
	int32_t value0;
	float value1;
};
#pragma pack(pop)

class SerialComm {
public:
	// Opens the serial port on construction.
	// Throws std::exception if the port cannot be opened.
	explicit SerialComm(const std::string &port_name,
						uint32_t baudrate      = 115200,
						uint32_t timeout_ms    = 1000);

	~SerialComm();

	// Immediately send a Command to the ESP32.
	// Returns false if the full struct could not be written.
	bool sendData(const Command &cmd);

	// Return the most recently received SensorData (cached by update()).
	// Returns false if no packet has been successfully received yet.
	bool getData(SensorData &data) const;

	// Read one incoming SensorData packet and cache it.
	// Call this in your main loop at whatever frequency you like.
	// Returns true if a new packet was received, false on timeout or framing error.
	bool update();

private:
	static constexpr uint8_t SYNC_BYTE_0 = 0xAA;
	static constexpr uint8_t SYNC_BYTE_1 = 0x55;

	serial_cpp::Serial m_port;
	SensorData m_rx_data{};
	bool m_has_data = false;
};
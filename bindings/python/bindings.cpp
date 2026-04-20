
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "SerialComm/SerialComm.hpp"
#include "SerialComm/SerialConfig.hpp"

namespace py = pybind11;

PYBIND11_MODULE(SerialCommPython, m) {
	m.doc() = "Python bindings for SerialComm";

	py::class_<SensorData>(m, "SensorData")
		.def(py::init<>())
		.def_readwrite("iteration", &SensorData::iteration)
		.def_readwrite("timestamp_ms", &SensorData::timestamp_ms)
		.def_readwrite("position", &SensorData::position)
		.def_readwrite("velocity", &SensorData::velocity)
		.def_readwrite("torque", &SensorData::torque)
		.def_readwrite("current", &SensorData::current)
		.def_readwrite("loopTimeMotor", &SensorData::loopTimeMotor)
		.def_readwrite("loopTimeSerial", &SensorData::loopTimeSerial);

	py::class_<Command>(m, "Command")
		.def(py::init<>())
		.def_readwrite("command_type", &Command::command_type)
		.def_readwrite("value0", &Command::value0)
		.def_readwrite("value1", &Command::value1);

	py::enum_<DrivingMode>(m, "DrivingMode")
		.value("Disabled", DrivingMode::Disabled)
		.value("Torque", DrivingMode::Torque)
		.value("Velocity", DrivingMode::Velocity)
		.value("Position", DrivingMode::Position);


	py::enum_<CommandType>(m, "CommandType")
		.value("NoCommand", CommandType::NoCommand)
		.value("TorqueKp", CommandType::TorqueKp)
		.value("TorqueKi", CommandType::TorqueKi)
		.value("VelocityKp", CommandType::VelocityKp)
		.value("VelocityKi", CommandType::VelocityKi)
		.value("VelocityKd", CommandType::VelocityKd)
		.value("PositionKp", CommandType::PositionKp)
		.value("PositionKi", CommandType::PositionKi)
		.value("PositionKd", CommandType::PositionKd)
		.value("TorqueSetpoint", CommandType::TorqueSetpoint)
		.value("VelocitySetpoint", CommandType::VelocitySetpoint)
		.value("PositionSetpoint", CommandType::PositionSetpoint)
		.value("DrivingModeCommand", CommandType::DrivingModeCommand);

	py::class_<SerialComm>(m, "SerialComm")
		.def(py::init<const std::string&, uint32_t, uint32_t>(),
			 py::arg("port_name"),
			 py::arg("baudrate") = 115200,
			 py::arg("timeout_ms") = 1000)

		.def("send_data", &SerialComm::sendData,
			 py::arg("cmd"))

		// getData: wrap output parameter -> return tuple
		.def("get_data",
			[](SerialComm &self) {
				SensorData data{};
				bool success = self.getData(data);
				return py::make_tuple(success, data);
			}
		);
}
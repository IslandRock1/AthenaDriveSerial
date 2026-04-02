
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "SerialComm/SerialComm.hpp"

namespace py = pybind11;

PYBIND11_MODULE(SerialCommPython, m) {
	m.doc() = "Python bindings for SerialComm";

	py::class_<SensorData>(m, "SensorData")
		.def(py::init<>())
		.def_readwrite("iteration", &SensorData::iteration)
		.def_readwrite("timestamp_ms", &SensorData::timestamp_ms)
		.def_readwrite("position", &SensorData::position)
		.def_readwrite("velocity", &SensorData::velocity);

	py::class_<Command>(m, "Command")
		.def(py::init<>())
		.def_readwrite("command_type", &Command::command_type)
		.def_readwrite("value0", &Command::value0)
		.def_readwrite("value1", &Command::value1);

	py::class_<SerialComm>(m, "SerialComm")
		.def(py::init<const std::string&, uint32_t, uint32_t>(),
			 py::arg("port_name"),
			 py::arg("baudrate") = 115200,
			 py::arg("timeout_ms") = 1000)

		// sendData: straightforward
		.def("send_data", &SerialComm::sendData,
			 py::arg("cmd"))

		// update: straightforward
		.def("update", &SerialComm::update)

		// getData: wrap output parameter → return tuple
		.def("get_data",
			[](const SerialComm &self) {
				SensorData data;
				bool success = self.getData(data);
				return py::make_tuple(success, data);
			}
		);
}
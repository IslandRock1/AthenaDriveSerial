
import SerialCommPython

def main():
    serialComm = SerialCommPython.SerialComm("COM3")

    cmd: SerialCommPython.Command = SerialCommPython.Command()
    cmd.command_type = 1
    cmd.value0 = 0
    cmd.value1 = 0.0

    iteration = 0
    try:
        while (True):
            iteration += 1
            if (iteration % 100 == 0):
                serialComm.send_data(cmd)

            serialComm.update()
            data = serialComm.get_data()
            if (data[0]):
                sensorData: SerialCommPython.SensorData = data[1]
                print(f"{sensorData.iteration} => {sensorData.position}")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__": main()
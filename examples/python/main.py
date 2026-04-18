
from time import perf_counter

from SerialCommPython import SerialComm, SensorData, Command
import pg_widgets as pw

def main():
    serialComm = SerialComm("COM4", 460800)
    controlManager = pw.ControlManager()

    plotPos = pw.Plot((0.0, 0.0), (0.5, 0.33))
    plotPos.setTitle("Position")
    plotPos.setXLabel("Time (s)")
    plotPos.setYLabel("Position (rad)")
    controlManager["plotPos"] = plotPos

    plotVel = pw.Plot((0.0, 0.33), (0.5, 0.33))
    plotVel.setTitle("Velocity")
    plotVel.setXLabel("Time (s)")
    plotVel.setYLabel("Velocity (rad/s)")
    controlManager["plotVel"] = plotVel

    plotCurrent = pw.Plot((0.0, 0.66), (0.5, 0.33))
    plotCurrent.setTitle("Current")
    plotCurrent.setXLabel("Time (s)")
    plotCurrent.setYLabel("Current (mA)")
    controlManager["plotCurrent"] = plotCurrent

    controlManager["sensorText"] = pw.TextBoxes((0.5, 0.0), (0.5, 0.5), labels=["Position", "Velocity", "Torque", "Current"])

    labels = ["Setpoint", "Kp", "Ki", "Kd"]
    upper_bounds = [-50.0, 0.0, 0.0, 0.0]
    lower_bounds = [50.0, 0.05, 0.0000015, 0.0000001]
    current_vals = [0.0, 0.005, 0.000000, 0.0]
    controlManager["tuningSlider"] = pw.TuningSliders((0.5, 0.5), (0.5, 0.5),
        labels=labels, lower_bounds=lower_bounds, upper_bounds=upper_bounds, current_values=current_vals)

    cmd = Command()
    prevSendTime = perf_counter()
    while controlManager.isRunning():
        if (perf_counter() - prevSendTime > 0.1):
            prevSendTime = perf_counter()
            values = controlManager["tuningSlider"].getValue()
            for ix, v in enumerate(values):
                cmd.command_type = ix + 1
                cmd.value1 = v
                serialComm.send_data(cmd)

        didGetData, prevData = serialComm.get_data()

        if (didGetData):
            data: SensorData
            texts = []
            texts.append(f"Position: {prevData.position:.3f}")
            texts.append(f"Velocity: {prevData.velocity:.3f}")
            texts.append(f"Torque: {prevData.torque:.3f}")
            texts.append(f"Current: {prevData.current:.3f}")
            controlManager["sensorText"].setTexts(texts)

            currTime = perf_counter()
            controlManager["plotPos"].addValue(currTime, prevData.position, maxLength=1000)
            controlManager["plotVel"].addValue(currTime, prevData.velocity, maxLength=1000)
            controlManager["plotCurrent"].addValue(currTime, prevData.current, maxLength=1000)

        renderTime = controlManager.getRenderTime()
        print(f"Rendertime: {renderTime}")
        controlManager.update()
        serialComm.update()

if __name__ == "__main__": main()
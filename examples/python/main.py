
from time import perf_counter

from SerialCommPython import SerialComm, SensorData, Command
import pg_widgets as pw

def main():
    serialComm = SerialComm("COM3", 460800)
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

    controlManager["sensorText"] = pw.TextBoxes((0.5, 0.0), (0.25, 0.5), labels=["Position", "Velocity", "Torque", "Current"])
    groupToggle = pw.UIGroup((0.75, 0.0), (0.25, 0.5))
    groupToggle["OnOffText"] = pw.TextBox((0.0, 0.0), (1.0, 0.25))
    groupToggle["OnOffText"].setText("Off / On")
    groupToggle["posText"] = pw.TextBox((0.0, 0.25), (0.5, 0.25))
    groupToggle["posText"].setText("Position")
    groupToggle["velText"] = pw.TextBox((0.0, 0.5), (0.5, 0.25))
    groupToggle["velText"].setText("Velocity")
    groupToggle["torText"] = pw.TextBox((0.0, 0.75), (0.5, 0.25))
    groupToggle["torText"].setText("Torque")
    groupToggle["posToggle"] = pw.ToggleButton((0.5, 0.25), (0.5, 0.25))
    groupToggle["velToggle"] = pw.ToggleButton((0.5, 0.5), (0.5, 0.25))
    groupToggle["torToggle"] = pw.ToggleButton((0.5, 0.75), (0.5, 0.25))

    controlManager["configGroup"] = groupToggle

    labels = ["Setpoint", "Kp", "Ki", "Kd"]
    upper_bounds = [-5.0, 0.0, 0.0, 0.0]
    lower_bounds = [5.0, 0.5, 0.0000015, 0.0000001]
    current_vals = [0.0, 0.005, 0.000000, 0.0]
    controlManager["tuningSlider"] = pw.TuningSliders((0.5, 0.5), (0.5, 0.5),
        labels=labels, lower_bounds=lower_bounds, upper_bounds=upper_bounds, current_values=current_vals)

    sliderIx = 0
    cmd = Command()
    cmd.command_type = 12
    cmd.value0 = 3
    serialComm.send_data(cmd)

    while controlManager.isRunning():
        if (serialComm.has_sent_data()):
            configType = 0
            if (controlManager["configGroup"]["posToggle"].getValue()):
                # PositionConfig
                configType = 1
            elif (controlManager["configGroup"]["velToggle"].getValue()):
                # VelocityConfig
                configType = 2
            elif (controlManager["configGroup"]["torToggle"].getValue()):
                # TorqueConfig
                configType = 3

            valueType = 0
            if (sliderIx == 0):
                # Setpoint
                valueType = 1
            elif (sliderIx == 1):
                # Kp
                valueType = 2
            elif (sliderIx == 2):
                # Ki
                valueType = 3
            elif (sliderIx == 3):
                # Kd
                valueType = 4

            values = controlManager["tuningSlider"].getValue()
            v = values[sliderIx]

            if (valueType == 0) or (configType == 0):
                cmd.command_type = 0
            elif (valueType == 1):
                # Setpoint
                cmd.command_type = 9
                if (configType == 1): cmd.command_type += 2
                elif (configType == 2): cmd.command_type += 1
                elif (configType == 3): cmd.command_type += 0
            elif (configType == 1):
                cmd.command_type = 4 + valueType
            elif (configType == 2):
                cmd.command_type = 1 + valueType
            elif (configType == 3) and (valueType != 4):
                cmd.command_type = -1 + valueType

            print(f"Config Type: {configType} | Value type: {valueType} | CMD: {cmd.command_type} | Value: {v}")
            cmd.value1 = v
            serialComm.send_data(cmd)

            sliderIx += 1
            if (sliderIx == len(values)):
                sliderIx = 0

        didGetData, prevData = serialComm.get_data()

        if (didGetData):
            data: SensorData
            texts = []
            texts.append(f"Position: {prevData.position:.3f}")
            texts.append(f"Velocity: {prevData.velocity:.3f}")
            texts.append(f"Torque: {prevData.torque}")
            texts.append(f"Current: {prevData.current:.3f}")
            controlManager["sensorText"].setTexts(texts)

            currTime = perf_counter()
            controlManager["plotPos"].addValue(currTime, prevData.position, maxLength=1000)
            controlManager["plotVel"].addValue(currTime, prevData.velocity, maxLength=1000)
            controlManager["plotCurrent"].addValue(currTime, prevData.current, maxLength=1000)

        renderTime = controlManager.getRenderTime()
        # print(f"Rendertime: {renderTime}")
        controlManager.update()

if __name__ == "__main__": main()
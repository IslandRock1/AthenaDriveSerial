
from time import perf_counter, sleep

from SerialCommPython import SerialComm, SensorData, Command, CommandType, DrivingMode
import pg_widgets as pw

def getPlotPos():
    plotPos = pw.Plot((0.0, 0.0), (0.5, 0.33))
    plotPos.setTitle("Position")
    plotPos.setXLabel("Time (s)")
    plotPos.setYLabel("Position (rad)")
    return plotPos

def getPlotVel():
    plotVel = pw.Plot((0.0, 0.33), (0.5, 0.33))
    plotVel.setTitle("Velocity")
    plotVel.setXLabel("Time (s)")
    plotVel.setYLabel("Velocity (rad/s)")
    return plotVel

def getPlotCurrent():
    plotCurrent = pw.Plot((0.0, 0.66), (0.5, 0.33))
    plotCurrent.setTitle("Current")
    plotCurrent.setXLabel("Time (s)")
    plotCurrent.setYLabel("Current (mA)")
    return plotCurrent

def getTextBoxesDriverData():
    labelsDescription = [
        "Iteration",
        "Timestamps (ms): ",
        "Position: ", "Velocity: ", "Torque: ", "Current: ",
        "Loop Motor (us): ",
        "Loop Comm (us): "
    ]
    labelsData = ["0"] * len(labelsDescription)
    textBoxesDescription = pw.TextBoxes((0.5, 0.0), (0.25, 0.5), labels=labelsDescription)
    textBoxesData = pw.TextBoxes((0.75, 0.0), (0.25, 0.5), labels=labelsData)
    return textBoxesDescription, textBoxesData

def getTuningSliders(name):
    labels = ["Setpoint", "Kp", "Ki", "Kd"]

    upper_bounds = [0.0] * 4
    lower_bounds = [0.0] * 4
    current_vals = [0.0] * 4
    if (name == "Position"):
        upper_bounds = [-10.0, 0.0, 0.0, 0.0]
        lower_bounds = [10.0, 5.0, 0.0, 0.0]
        current_vals = [0.0, 0.000, 0.000000, 0.0]
    elif (name == "Velocity"):
        upper_bounds = [-30.0, 0.0, 0.0, 0.0]
        lower_bounds = [30.0, 0.1, 0.000001, 0.0]
        current_vals = [0.0, 0.03, 0.000000, 0.0]
    elif (name == "Torque"):
        upper_bounds = [-0.5, 0.0, 0.0, 0.0]
        lower_bounds = [0.5, 0.005, 0.0, 0.0]
        current_vals = [0.0, 0.000, 0.000000, 0.0]

    slider = pw.TuningSliders((0.5, 0.5), (0.5, 0.45),
        labels=labels, lower_bounds=lower_bounds, upper_bounds=upper_bounds, current_values=current_vals)
    return slider

def generateTab(name):
    # Making a tab for tuning, having 3x plots on the left
    # Feedback text and tuning sliders on the right.

    gr = pw.UIGroup((0.0, 0.0), (1.0, 1.0))
    gr[f"{name}plotPos"] = getPlotPos()
    gr[f"{name}plotVel"] = getPlotVel()
    gr[f"{name}plotCurrent"] = getPlotCurrent()

    descriptionBoxes, dataBoxes = getTextBoxesDriverData()
    gr["textBoxesDescription"] = descriptionBoxes
    gr[f"{name}textBoxesData"] = dataBoxes
    gr[f"{name}TuningSliders"] = getTuningSliders(name)

    gr["nameText"] = pw.TextBox((0.5, 0.95), (0.3, 0.05))
    gr["nameText"].setText(name)
    return gr

def generateMainTab(name):
    gr = pw.UIGroup((0.0, 0.0), (1.0, 1.0))
    gr["plotPos"] = getPlotPos()
    gr["plotVel"] = getPlotVel()
    gr["plotCurrent"] = getPlotCurrent()

    descriptionBoxes, dataBoxes = getTextBoxesDriverData()
    gr["textBoxesDescription"] = descriptionBoxes
    gr[f"{name}textBoxesData"] = dataBoxes

    gr["textOnOff"] = pw.TextBox((0.5, 0.5), (0.5, 0.1))
    gr["textOnOff"].setText("Driving Mode (off / on)")

    gr["descriptions"] = pw.TextBoxes((0.5, 0.6), (0.25, 0.35), labels = ["Position", "Velocity", "Torque"])
    gr["togglePos"] = pw.ToggleButton((0.75, 0.6), (0.25, 0.1166666))
    gr["toggleVel"] = pw.ToggleButton((0.75, 0.7166666), (0.25, 0.1166666))
    gr["toggleTor"] = pw.ToggleButton((0.75, 0.8333333), (0.25, 0.1166666))

    gr["nameText"] = pw.TextBox((0.5, 0.95), (0.3, 0.05))
    gr["nameText"].setText(name)

    return gr

def main():
    enableSerial = True

    if enableSerial: serialComm = SerialComm("COM3", 460800)
    controlManager = pw.ControlManager()

    mainTab = generateMainTab("Main")
    posTab = generateTab("Position")
    velTab = generateTab("Velocity")
    torTab = generateTab("Torque")
    tabs = pw.Tab((0.0, 0.0), (1.0, 1.0), [mainTab, posTab, velTab, torTab])
    controlManager["tabs"] = tabs

    prevValues = {}
    baseTime = perf_counter()
    def getIfDelta(name, value):
        if (name in prevValues):
            if (prevValues[name] == value): return False
        prevValues[name] = value
        return True

    while controlManager.isRunning():

        if enableSerial:
            didGetData, data = serialComm.get_data()
            if (didGetData):
                data: SensorData

                texts = [f"{data.iteration}", f"{data.timestamp_ms}", f"{data.position}", f"{data.velocity}", f"{data.torque}", f"{data.current}", f"{data.loopTimeMotor}", f"{data.loopTimeSerial}"]
                controlManager["PositiontextBoxesData"].setTexts(texts)
                controlManager["VelocitytextBoxesData"].setTexts(texts)
                controlManager["TorquetextBoxesData"].setTexts(texts)
                controlManager["MaintextBoxesData"].setTexts(texts)

                timeNow = round(perf_counter() - baseTime, 2)
                for name in ["Position", "Velocity", "Torque"]:
                    numPoints = 100
                    controlManager[f"{name}plotPos"].addValue(timeNow, data.position, maxLength=numPoints)
                    controlManager[f"{name}plotVel"].addValue(timeNow, data.velocity, maxLength=numPoints)
                    controlManager[f"{name}plotCurrent"].addValue(timeNow, data.current, maxLength=numPoints)


        togNames = ["togglePos", "toggleVel", "toggleTor"]
        commandValues = [DrivingMode.Position, DrivingMode.Velocity, DrivingMode.Torque]
        for name, valueDefault in zip(togNames, commandValues):
            state = controlManager[name].getValue()
            if (getIfDelta(name, state)):
                value = valueDefault if state else DrivingMode.Disabled
                cmd = Command(CommandType.DrivingModeCommand, value)
                print(f"Setting driving mode to: {value}")
                if enableSerial: serialComm.send_data(cmd)

        for tuningName, baseCommand in zip(["Position", "Velocity", "Torque"], [CommandType.PositionSetpoint, CommandType.VelocitySetpoint, CommandType.TorqueSetpoint]):
            values = controlManager[tuningName + "TuningSliders"].getValue()
            # Setpoint, Kp, Ki, Kd (no Kd for torque)
            for ix in range(4):
                v = values[ix]
                if getIfDelta(f"{tuningName}{ix}", v):
                    cmd = Command(baseCommand.value + ix, 0, v)
                    print(f"Sending {v} to {baseCommand.value + ix}")
                    if enableSerial: serialComm.send_data(cmd)


        renderTime = controlManager.getRenderTime()
        # print(f"Rendertime: {renderTime}")
        controlManager.update()

    cmd = Command(CommandType.DrivingModeCommand, DrivingMode.Disabled)
    serialComm.send_data(cmd)

    if (serialComm.num_remaining_commands() > 0): print("Disabling motor.")
    while (serialComm.num_remaining_commands() > 0):
        sleep(0.1)
    print("Motor successfully disabled")

if __name__ == "__main__": main()

from time import perf_counter, sleep

import utils.plotUtils as pltUtil
from SerialCommPython import SerialComm, SensorData, Command, CommandType, DrivingMode
import pg_widgets as pw

def save_data_to_txt(
        filename,
        positionPoints,
        velocityPoints,
        acceleraPoints,
        phaseAPoints,
        phaseBPoints,
        phaseCPoints,
        motorLoopTime,
        commmLoopTime,
        timestamps
):
    # Find the longest list length
    max_len = max(
        len(positionPoints),
        len(velocityPoints),
        len(acceleraPoints),
        len(phaseAPoints),
        len(phaseBPoints),
        len(phaseCPoints),
        len(motorLoopTime),
        len(commmLoopTime),
        len(timestamps)
    )

    with open(filename, "w") as f:
        # Write header
        f.write(
            "timestamp\tposition\tvelocity\tacceleration\t"
            "phaseA\tphaseB\tphaseC\tmotorLoopTime\tcommLoopTime\n"
        )

        # Write data rows
        for i in range(max_len):
            row = [
                timestamps[i] if i < len(timestamps) else "",
                positionPoints[i] if i < len(positionPoints) else "",
                velocityPoints[i] if i < len(velocityPoints) else "",
                acceleraPoints[i] if i < len(acceleraPoints) else "",
                phaseAPoints[i] if i < len(phaseAPoints) else "",
                phaseBPoints[i] if i < len(phaseBPoints) else "",
                phaseCPoints[i] if i < len(phaseCPoints) else "",
                motorLoopTime[i] if i < len(motorLoopTime) else "",
                commmLoopTime[i] if i < len(commmLoopTime) else "",
            ]

            f.write("\t".join(map(str, row)) + "\n")

    print(f"Data saved to {filename}")

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
        "Timestamps (us): ",
        "Position (rad): ", "Velocity (rad/s): ", "Torque: ", "Current (mA): ", "Voltage (mV): ",
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
        upper_bounds = [0.0, 0.0, 0.0, 0.0]
        lower_bounds = [100, 5.0, 0.0001, 0.0]
        current_vals = [0.0, 0.0, 0.0, 0.0]
    elif (name == "Velocity"):
        upper_bounds = [-50.0, 0.0, 0.0, 0.0]
        lower_bounds = [50.0, 5.0, 0.00001, 0.0]
        current_vals = [0.0, 0.0, 0.0, 0.0]
    elif (name == "Torque"):
        upper_bounds = [-30.0, 0.0, 0.0, 0.0]
        lower_bounds = [30.0, 0.005, 0.0, 0.0]
        current_vals = [0.0, 0.0, 0.0, 0.0]
    elif (name == "OpenLoop"):
        labels = ["Speed", "Strength"]
        upper_bounds = [1.0, 1.0]
        lower_bounds = [-1.0, 0.0]
        current_vals = [0.0, 0.0]

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
    gr[f"{name}plotPos"] = getPlotPos()
    gr[f"{name}plotVel"] = getPlotVel()
    gr[f"{name}plotCurrent"] = getPlotCurrent()

    descriptionBoxes, dataBoxes = getTextBoxesDriverData()
    gr["textBoxesDescription"] = descriptionBoxes
    gr[f"{name}textBoxesData"] = dataBoxes

    gr["textOnOff"] = pw.TextBox((0.5, 0.5), (0.5, 0.1))
    gr["textOnOff"].setText("Driving Mode (off / on)")

    gr["descriptions"] = pw.TextBoxes((0.5, 0.6), (0.25, 0.35), labels = ["Position", "Velocity", "Torque", "OpenLoop"])
    gr["togglePos"] = pw.ToggleButton((0.75, 0.6 + 0.0875 * 0), (0.25, 0.0875))
    gr["toggleVel"] = pw.ToggleButton((0.75, 0.6 + 0.0875 * 1), (0.25, 0.0875))
    gr["toggleTor"] = pw.ToggleButton((0.75, 0.6 + 0.0875 * 2), (0.25, 0.0875))
    gr["toggleOpe"] = pw.ToggleButton((0.75, 0.6 + 0.0875 * 3), (0.25, 0.0875))

    gr["nameText"] = pw.TextBox((0.5, 0.95), (0.3, 0.05))
    gr["nameText"].setText(name)

    return gr

def main():
    enableSerial = True

    if enableSerial: serialComm = SerialComm("COM6", 460800)
    if enableSerial: serialComm.send_data(Command(CommandType.CurrentLimit, 3000))
    controlManager = pw.ControlManager()

    mainTab = generateMainTab("Main")
    posTab = generateTab("Position")
    velTab = generateTab("Velocity")
    torTab = generateTab("Torque")
    opeTab = generateTab("OpenLoop")
    tabs = pw.Tab((0.0, 0.0), (1.0, 1.0), [mainTab, posTab, velTab, torTab, opeTab])
    controlManager["tabs"] = tabs

    setpoints = {"Position": 0.0, "Velocity": 0.0}
    prevValues = {}
    baseTime = perf_counter()
    def getIfDelta(name, value):
        if (name in prevValues):
            if (prevValues[name] == value): return False
        prevValues[name] = value
        return True

    positionPoints = []
    velocityPoints = []
    acceleraPoints = []
    phaseAPoints = []
    phaseBPoints = []
    phaseCPoints = []
    motorLoopTime = []
    commmLoopTime = []
    timestamps = []

    while controlManager.isRunning():

        if enableSerial:
            didGetData, data = serialComm.get_data()
            if (didGetData):
                data: SensorData
                positionPoints.append(data.position)
                velocityPoints.append(data.velocity)
                acceleraPoints.append(data.acceleration)
                phaseAPoints.append(data.Ia)
                phaseBPoints.append(data.Ib)
                phaseCPoints.append(data.Ic)
                motorLoopTime.append(data.loopTimeMotor)
                commmLoopTime.append(data.loopTimeSerial)
                timestamps.append(perf_counter())

                # print(f"Ia: {data.Ia} | Ib: {data.Ib} | Ic: {data.Ic}")

                texts = [f"{data.iteration}", f"{data.timestamp_ms}", f"{data.position}", f"{data.velocity}", f"{data.torque}", f"{data.current}", f"{data.voltage}", f"{data.loopTimeMotor}", f"{data.loopTimeSerial}"]
                controlManager["PositiontextBoxesData"].setTexts(texts)
                controlManager["VelocitytextBoxesData"].setTexts(texts)
                controlManager["TorquetextBoxesData"].setTexts(texts)
                controlManager["OpenLooptextBoxesData"].setTexts(texts)
                controlManager["MaintextBoxesData"].setTexts(texts)

                timeNow = round(perf_counter() - baseTime, 2)
                for name in ["Main", "Position", "Velocity", "Torque", "OpenLoop"]:
                    numPoints = 1000
                    controlManager[f"{name}plotPos"].addValue(timeNow, data.position, maxLength=numPoints)
                    controlManager[f"{name}plotVel"].addValue(timeNow, data.velocity, maxLength=numPoints)
                    controlManager[f"{name}plotCurrent"].addValue(timeNow, data.current, maxLength=numPoints)

                    controlManager[f"{name}plotPos"].addValue(timeNow, setpoints["Position"], 1, maxLength=numPoints)
                    controlManager[f"{name}plotVel"].addValue(timeNow, setpoints["Velocity"], 1, maxLength=numPoints)


        togNames = ["togglePos", "toggleVel", "toggleTor", "toggleOpe"]
        commandValues = [DrivingMode.Position, DrivingMode.Velocity, DrivingMode.Torque, DrivingMode.OpenLoop]
        for name, valueDefault in zip(togNames, commandValues):
            state = controlManager[name].getValue()
            if (getIfDelta(name, state)):
                value = valueDefault if state else DrivingMode.Disabled
                cmd = Command(CommandType.DrivingModeCommand, value)
                print(f"Setting driving mode to: {value}")
                if enableSerial: serialComm.send_data(cmd)

        for tuningName, baseCommand in zip(["Position", "Velocity", "Torque"], [CommandType.PositionSetpoint, CommandType.VelocitySetpoint, CommandType.TorqueSetpoint]):
            values = controlManager[tuningName + "TuningSliders"].getValue()
            setpoints[tuningName] = values[0]
            # Setpoint, Kp, Ki, Kd (no Kd for torque)
            for ix in range(4):
                v = values[ix]

                if getIfDelta(f"{tuningName}{ix}", v):
                    cmd = Command(baseCommand.value + ix, 0, v)
                    print(f"Sending {v} to {baseCommand.value + ix}")
                    if enableSerial: serialComm.send_data(cmd)

        values = controlManager["OpenLoopTuningSliders"].getValue()
        if getIfDelta("openLoopSpeed", values[0]):
            print(f"Sending {values[0]} to {CommandType.OpenLoopSpeed.value}")
            cmd = Command(CommandType.OpenLoopSpeed, 0, values[0])
            if enableSerial: serialComm.send_data(cmd)

        if getIfDelta("openLoopStrength", values[1]):
            print(f"Sending {values[1]} to {CommandType.OpenLoopStrength.value}")
            cmd = Command(CommandType.OpenLoopStrength, 0, values[1])
            if enableSerial: serialComm.send_data(cmd)

        renderTime = controlManager.getRenderTime()
        # print(f"Rendertime: {renderTime}")
        controlManager.update()

    if enableSerial:
        cmd = Command(CommandType.DrivingModeCommand, DrivingMode.Disabled)
        serialComm.send_data(cmd)

        if (serialComm.num_remaining_commands() > 0): print("Disabling motor.")
        while (serialComm.num_remaining_commands() > 0):
            sleep(0.1)
    print("Motor successfully disabled")

    print("Creating plots.")
    pltUtil.plot_encoder_state_estimation(timestamps, positionPoints, velocityPoints, acceleraPoints)
    pltUtil.plot_phase_currents(timestamps, phaseAPoints, phaseBPoints, phaseCPoints)
    pltUtil.plot_loop_times(timestamps, motorLoopTime, commmLoopTime)

    save_data_to_txt(f"Test{perf_counter()}", positionPoints, velocityPoints, acceleraPoints,
                     phaseAPoints, phaseBPoints, phaseCPoints, motorLoopTime, commmLoopTime, timestamps)

if __name__ == "__main__": main()
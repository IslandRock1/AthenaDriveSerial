
from time import perf_counter

from SerialCommPython import SerialComm, SensorData, Command
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

def getTuningSliders():
    labels = ["Setpoint", "Kp", "Ki", "Kd"]
    upper_bounds = [-5.0, 0.0, 0.0, 0.0]
    lower_bounds = [5.0, 0.5, 0.0000015, 0.0000001]
    current_vals = [0.0, 0.005, 0.000000, 0.0]
    slider = pw.TuningSliders((0.5, 0.5), (0.5, 0.45),
        labels=labels, lower_bounds=lower_bounds, upper_bounds=upper_bounds, current_values=current_vals)
    return slider

def generateTab(name):
    # Making a tab for tuning, having 3x plots on the left
    # Feedback text and tuning sliders on the right.

    gr = pw.UIGroup((0.0, 0.0), (1.0, 1.0))
    gr["plotPos"] = getPlotPos()
    gr["plotVel"] = getPlotVel()
    gr["plotCurrent"] = getPlotCurrent()

    descriptionBoxes, dataBoxes = getTextBoxesDriverData()
    gr["textBoxesDescription"] = descriptionBoxes
    gr["textBoxesData"] = dataBoxes
    gr["tuningSliders"] = getTuningSliders()

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
    gr["textBoxesData"] = dataBoxes

    gr["textOnOff"] = pw.TextBox((0.5, 0.5), (0.5, 0.1))
    gr["textOnOff"].setText("Driving Mode (on / off)")

    gr["descriptions"] = pw.TextBoxes((0.5, 0.6), (0.25, 0.35), labels = ["Position", "Velocity", "Torque"])
    gr["togglePos"] = pw.ToggleButton((0.75, 0.6), (0.25, 0.1166666))
    gr["toggleVel"] = pw.ToggleButton((0.75, 0.7166666), (0.25, 0.1166666))
    gr["toggleTor"] = pw.ToggleButton((0.75, 0.8333333), (0.25, 0.1166666))

    gr["nameText"] = pw.TextBox((0.5, 0.95), (0.3, 0.05))
    gr["nameText"].setText(name)

    return gr

def main():
    enableSerial = False

    if enableSerial: serialComm = SerialComm("COM4", 460800)
    controlManager = pw.ControlManager()

    mainTab = generateMainTab("Main")
    posTab = generateTab("Position")
    velTab = generateTab("Velocity")
    torTab = generateTab("Torque")
    tabs = pw.Tab((0.0, 0.0), (1.0, 1.0), [mainTab, posTab, velTab, torTab])
    controlManager["tabs"] = tabs

    prevValues = {}

    while controlManager.isRunning():

        if enableSerial:
            didGetData, prevData = serialComm.get_data()
            if (didGetData):
                data: SensorData

        renderTime = controlManager.getRenderTime()
        # print(f"Rendertime: {renderTime}")
        controlManager.update()

if __name__ == "__main__": main()
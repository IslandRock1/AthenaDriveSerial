
/*
THIS COMPLETE FILE IS CREATED BY CLAUD AI.
 */


#include <iostream>
#include <chrono>
#include <cmath>
#include <thread>
#include <string>
#include "SerialComm/SerialComm.hpp"

// --- Helpers -----------------------------------------------------------

using Clock     = std::chrono::high_resolution_clock;
using Ms        = std::chrono::milliseconds;
using TimePoint = std::chrono::time_point<Clock>;

static double secondsSince(const TimePoint& t0) {
    return std::chrono::duration_cast<std::chrono::microseconds>(
               Clock::now() - t0).count() / 1e6;
}

// Wait until the send-buffer has drained to at most `threshold` commands.
// Prints a dot every 100 ms so the user knows we're alive.
static void waitForBuffer(SerialComm& sc, int threshold = 0) {
    while (sc.getNumRemainingCommands() > threshold) {
        std::this_thread::sleep_for(Ms(100));
        std::cout << '.' << std::flush;
    }
    std::cout << '\n';
}

// Queue a command and (optionally) print what we sent.
static void send(SerialComm& sc, Command cmd, const std::string& label = "") {
    sc.sendData(cmd);
    if (!label.empty())
        std::cout << "  [CMD] " << label << '\n';
}

// --- Phase helpers -----------------------------------------------------

// Set PID gains for a given mode in one go.
static void setPID(SerialComm& sc,
                   CommandType kp, CommandType ki, CommandType kd,
                   float Kp, float Ki, float Kd,
                   const std::string& modeName) {
    Command cmd{};
    cmd.command_type = kp;  cmd.value1 = Kp;  sc.sendData(cmd);
    cmd.command_type = ki;  cmd.value1 = Ki;  sc.sendData(cmd);
    cmd.command_type = kd;  cmd.value1 = Kd;  sc.sendData(cmd);
    std::cout << "  [PID] " << modeName
              << "  Kp=" << Kp << "  Ki=" << Ki << "  Kd=" << Kd << '\n';
}

// Print one line of sensor data.
static void printSensor(const SensorData& d) {
    std::cout << "  iter=" << d.iteration
              << "  t="        << d.timestamp_ms  << " ms"
              << "  pos="      << d.position       << " rad"
              << "  vel="      << d.velocity       << " rad/s"
              << "  torque="   << d.torque         << " Nm"
              << "  current="  << d.current        << " A"
              << "  voltage="  << d.voltage        << " V"
              << "  tMotor="   << d.loopTimeMotor  << " us"
              << "  tSerial="  << d.loopTimeSerial << " us"
              << '\n';
}

// -----------------------------------------------------------------------
// PHASE 1 – Torque mode: sine-wave torque for ~4 s
// -----------------------------------------------------------------------
static void phaseTorque(SerialComm& sc) {
    std::cout << "\n=== PHASE 1: Torque mode (sine wave, 4 s) ===\n";

    Command cmd{};

    // Safety first: zero torque before switching mode
    cmd.command_type = CommandType::TorqueSetpoint;
    cmd.value1 = 0.0f;
    send(sc, cmd, "TorqueSetpoint = 0 (pre-switch safety)");

    // Tune torque-loop PID
    setPID(sc,
           CommandType::TorqueKp, CommandType::TorqueKi, CommandType::TorqueKd,
           1.0f, 0.05f, 0.0f, "Torque");

    // Set current limit
    cmd.command_type = CommandType::SetCurrentLimit;
    cmd.value1 = 5.0f;   // 5 A
    send(sc, cmd, "CurrentLimit = 5 A");

    // Switch to torque driving mode
    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Torque;
    cmd.value1 = 0.0f;
    send(sc, cmd, "DrivingMode = Torque");

    waitForBuffer(sc);   // Let the board process the config commands first

    // Stream a sine-wave torque setpoint for 4 seconds
    const double duration  = 4.0;
    const double amplitude = 0.2;   // Nm
    const double freq      = 0.5;   // Hz

    SensorData data{};
    auto t0          = Clock::now();
    auto prevSend    = t0;
    auto prevPrint   = t0;

    cmd.command_type = CommandType::TorqueSetpoint;

    while (secondsSince(t0) < duration) {
        double now = secondsSince(t0);

        // Queue a new setpoint every 50 ms (much slower than the 10 ms
        // board cycle, so we never flood the buffer)
        if (std::chrono::duration_cast<Ms>(Clock::now() - prevSend).count() >= 50) {
            prevSend = Clock::now();
            cmd.value1 = static_cast<float>(amplitude * std::sin(2.0 * M_PI * freq * now));
            sc.sendData(cmd);
        }

        sc.getData(data);

        if (std::chrono::duration_cast<Ms>(Clock::now() - prevPrint).count() >= 200) {
            prevPrint = Clock::now();
            std::cout << "  t=" << now << " s  buf=" << sc.getNumRemainingCommands();
            printSensor(data);
        }

        std::this_thread::sleep_for(Ms(1));
    }

    // Zero torque before leaving
    cmd.value1 = 0.0f;
    send(sc, cmd, "TorqueSetpoint = 0 (end of phase)");
    waitForBuffer(sc);
}

// -----------------------------------------------------------------------
// PHASE 2 – Velocity mode: step changes every second for ~6 s
// -----------------------------------------------------------------------
static void phaseVelocity(SerialComm& sc) {
    std::cout << "\n=== PHASE 2: Velocity mode (step changes, 6 s) ===\n";

    Command cmd{};

    // Zero the setpoint first
    cmd.command_type = CommandType::VelocitySetpoint;
    cmd.value1 = 0.0f;
    send(sc, cmd, "VelocitySetpoint = 0 (pre-switch safety)");

    setPID(sc,
           CommandType::VelocityKp, CommandType::VelocityKi, CommandType::VelocityKd,
           2.0f, 0.1f, 0.01f, "Velocity");

    cmd.command_type = CommandType::SetCurrentLimit;
    cmd.value1 = 8.0f;
    send(sc, cmd, "CurrentLimit = 8 A");

    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Velocity;
    cmd.value1 = 0.0f;
    send(sc, cmd, "DrivingMode = Velocity");

    waitForBuffer(sc);

    // Step sequence: [rad/s, duration_s]
    const std::pair<float, double> steps[] = {
        { 2.0f, 1.5},
        {-2.0f, 1.5},
        { 5.0f, 1.5},
        { 0.0f, 1.5},
    };

    SensorData data{};
    cmd.command_type = CommandType::VelocitySetpoint;

    for (auto& [target, dur] : steps) {
        cmd.value1 = target;
        send(sc, cmd, "VelocitySetpoint = " + std::to_string(target) + " rad/s");

        auto t0    = Clock::now();
        auto prevP = t0;
        while (secondsSince(t0) < dur) {
            sc.getData(data);
            if (std::chrono::duration_cast<Ms>(Clock::now() - prevP).count() >= 200) {
                prevP = Clock::now();
                std::cout << "  buf=" << sc.getNumRemainingCommands();
                printSensor(data);
            }
            std::this_thread::sleep_for(Ms(1));
        }
    }

    waitForBuffer(sc);
}

// -----------------------------------------------------------------------
// PHASE 3 – Position mode: multi-point trajectory over ~8 s
// -----------------------------------------------------------------------
static void phasePosition(SerialComm& sc) {
    std::cout << "\n=== PHASE 3: Position mode (trajectory, 8 s) ===\n";

    Command cmd{};

    cmd.command_type = CommandType::PositionSetpoint;
    cmd.value1 = 0.0f;
    send(sc, cmd, "PositionSetpoint = 0 (pre-switch safety)");

    setPID(sc,
           CommandType::PositionKp, CommandType::PositionKi, CommandType::PositionKd,
           10.0f, 0.2f, 0.5f, "Position");

    cmd.command_type = CommandType::SetCurrentLimit;
    cmd.value1 = 10.0f;
    send(sc, cmd, "CurrentLimit = 10 A");

    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Position;
    cmd.value1 = 0.0f;
    send(sc, cmd, "DrivingMode = Position");

    waitForBuffer(sc);

    // Trajectory waypoints: [position_rad, dwell_s]
    const std::pair<float, double> waypoints[] = {
        { static_cast<float>( M_PI / 2.0), 2.0},   //  90°
        { static_cast<float>(-M_PI / 2.0), 2.0},   // -90°
        { static_cast<float>( M_PI),       2.0},   // 180°
        { 0.0f,                            2.0},   //   0° (home)
    };

    SensorData data{};
    cmd.command_type = CommandType::PositionSetpoint;

    for (auto& [target, dwell] : waypoints) {
        cmd.value1 = target;
        send(sc, cmd, "PositionSetpoint = " + std::to_string(target * 180.0f / static_cast<float>(M_PI)) + " deg");

        auto t0    = Clock::now();
        auto prevP = t0;
        while (secondsSince(t0) < dwell) {
            sc.getData(data);
            if (std::chrono::duration_cast<Ms>(Clock::now() - prevP).count() >= 200) {
                prevP = Clock::now();
                float err = target - data.position;
                std::cout << "  buf=" << sc.getNumRemainingCommands()
                          << "  posErr=" << err << " rad";
                printSensor(data);
            }
            std::this_thread::sleep_for(Ms(1));
        }
    }

    waitForBuffer(sc);
}

// -----------------------------------------------------------------------
// PHASE 4 – Live PID re-tune demo (position mode)
//   Queues a burst of gain-change commands, then watches the buffer drain.
// -----------------------------------------------------------------------
static void phaseRetune(SerialComm& sc) {
    std::cout << "\n=== PHASE 4: Live re-tune demo (position mode) ===\n";

    // Stay in position mode, hold position at pi/4
    Command cmd{};
    cmd.command_type = CommandType::PositionSetpoint;
    cmd.value1 = static_cast<float>(M_PI / 4.0);
    send(sc, cmd, "PositionSetpoint = 45 deg (hold)");

    // Queue a sequence of Kp sweeps — each takes ~10 ms to reach the board
    const float kpValues[] = {5.0f, 15.0f, 25.0f, 10.0f};
    for (float kp : kpValues) {
        cmd.command_type = CommandType::PositionKp;
        cmd.value1 = kp;
        sc.sendData(cmd);
        std::cout << "  [QUEUE] PositionKp = " << kp
                  << "  (buffer depth now " << sc.getNumRemainingCommands() << ")\n";
    }

    std::cout << "  Waiting for buffer to drain";
    waitForBuffer(sc);

    SensorData data{};
    auto t0 = Clock::now();
    while (secondsSince(t0) < 2.0) {
        sc.getData(data);
        std::this_thread::sleep_for(Ms(200));
    }
    printSensor(data);
}

// -----------------------------------------------------------------------
// Shutdown: zero everything and disable
// -----------------------------------------------------------------------
static void shutdown(SerialComm& sc) {
    std::cout << "\n=== SHUTDOWN: zeroing setpoints and disabling ===\n";

    Command cmd{};
    cmd.command_type = CommandType::TorqueSetpoint;   cmd.value1 = 0.0f; sc.sendData(cmd);
    cmd.command_type = CommandType::VelocitySetpoint; cmd.value1 = 0.0f; sc.sendData(cmd);
    cmd.command_type = CommandType::PositionSetpoint; cmd.value1 = 0.0f; sc.sendData(cmd);

    cmd.command_type = CommandType::DrivingModeCommand;
    cmd.value0 = DrivingMode::Disabled;
    cmd.value1 = 0.0f;
    send(sc, cmd, "DrivingMode = Disabled");

    waitForBuffer(sc);
    std::cout << "Motor safely disabled.\n";
}

// -----------------------------------------------------------------------
int main() {
    // SerialComm serialComm("/dev/ttyACM0");   // Linux / macOS
    SerialComm serialComm("COM4");              // Windows

    std::cout << "Connected. Running full protocol demo.\n";

    phaseTorque(serialComm);
    phaseVelocity(serialComm);
    phasePosition(serialComm);
    phaseRetune(serialComm);
    shutdown(serialComm);

    std::cout << "\nDemo complete.\n";
    return 0;
}
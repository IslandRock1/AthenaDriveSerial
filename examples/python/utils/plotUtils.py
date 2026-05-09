
import matplotlib.pyplot as plt
import numpy as np

def plot_encoder_state_estimation(
        timestamps,
        position,
        velocity,
        acceleration,
        title="State Estimation with Encoder"
):

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Position plot
    axes[0].plot(timestamps, position)
    axes[0].set_ylabel("Position")
    axes[0].set_title(title)
    axes[0].grid(True)

    # Velocity plot
    axes[1].plot(timestamps, velocity)
    axes[1].set_ylabel("Velocity")
    axes[1].grid(True)

    # Acceleration plot
    axes[2].plot(timestamps, acceleration)
    axes[2].set_ylabel("Acceleration")
    axes[2].set_xlabel("Time [s]")
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()

def plot_phase_currents(
        timestamps,
        current_a,
        current_b,
        current_c,
        title="Three-Phase Current Measurements"
):

    # Compute current sum
    current_sum = (
            np.asarray(current_a)
            + np.asarray(current_b)
            + np.asarray(current_c)
    )

    fig, axes = plt.subplots(
        2, 1,
        figsize=(10, 7),
        sharex=True
    )

    # Phase currents
    axes[0].plot(timestamps, current_a, label="Phase A")
    axes[0].plot(timestamps, current_b, label="Phase B")
    axes[0].plot(timestamps, current_c, label="Phase C")

    axes[0].set_ylabel("Current [A]")
    axes[0].set_title(title)
    axes[0].legend()
    axes[0].grid(True)

    # Sum of currents
    axes[1].plot(
        timestamps,
        current_sum,
    )

    axes[1].set_ylabel("Sum Current [A]")
    axes[1].set_xlabel("Time [s]")
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()

def plot_loop_times(
        timestamps,
        motor_loop_time,
        communication_loop_time,
        title="Control Loop Timing"
):

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Left y-axis: motor loop
    line1 = ax1.plot(
        timestamps,
        motor_loop_time,
        label="Motor Loop Time",
        color="tab:blue"
    )

    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Motor Loop Time [us]", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.grid(True)

    # Right y-axis: communication loop
    ax2 = ax1.twinx()

    line2 = ax2.plot(
        timestamps,
        communication_loop_time,
        label="Communication Loop Time",
        color="tab:red"
    )

    ax2.set_ylabel("Communication Loop Time [us]", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    # Combined legend
    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels)

    plt.title(title)
    plt.tight_layout()
    plt.show()

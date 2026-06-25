import time
import random
import numpy as np
import pygame
from pylsl import StreamInfo, StreamOutlet

# --- Configuration ---
FS = 44100
BEEP_FREQ = 600
BEEP_DURATION = 0.15  # Short cue beep marking task start/stop (seconds)

# Stimulus / marker codes
REST = 0
PASSIVE_FAST = 1
PASSIVE_SLOW = 2
STIM_DICT = {REST: "Rest", PASSIVE_FAST: "Passive Fast", PASSIVE_SLOW: "Passive Slow"}
TASKS = [PASSIVE_FAST, PASSIVE_SLOW]

# Randomized interval ranges (seconds)
REST_RANGE = (30, 31)
STIM_RANGE = (179, 180)

# Initialize Pygame Mixer
pygame.mixer.init(frequency=FS, size=-16, channels=2)

# --- LSL Setup ---
info = StreamInfo("Trigger", "Markers", 1, 0, "int32", "auditory_trial_001")
outlet = StreamOutlet(info)


def get_beep_sound(duration, frequency=BEEP_FREQ, fs=FS):
    """Generates a sine wave and returns a pygame Sound object."""
    t = np.linspace(0, duration, int(fs * duration), False)
    # Smooth edges to prevent 'popping'
    fade = min(int(fs * 0.01), len(t) // 2)
    envelope = np.ones_like(t)
    if fade > 0:
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)

    # Generate 16-bit PCM audio (reshape to 2D for pygame)
    samples = (np.sin(frequency * t * 2 * np.pi) * 32767 * 0.5 * envelope).astype(
        np.int16
    )
    samples = np.column_stack([samples, samples])
    return pygame.sndarray.make_sound(samples)


# Pre-generate the short cue beep once so it never "keeps going".
CUE_BEEP = get_beep_sound(BEEP_DURATION)


def beep():
    """Play a short cue beep and block until it finishes."""
    CUE_BEEP.play()
    time.sleep(BEEP_DURATION)


N_TRIALS = 1


def select_task():
    """Prompt the user to choose which stimulus to send for this recording."""
    while True:
        choice = input("Select stimulus  [1] Passive Fast  [2] Passive Slow : ").strip()
        if choice in ("1", "2"):
            task = int(choice)
            print(f"Stimulus set to: {STIM_DICT[task]}")
            return task
        print("Invalid choice, enter 1 or 2.")


def rest_block():
    rest_duration = random.uniform(*REST_RANGE)
    print(f"Phase: {STIM_DICT[REST]} | Duration: {rest_duration:.2f}s")
    outlet.push_sample([REST])
    time.sleep(rest_duration)


def run_trial():
    print("Stream 'Trigger' initialized.")
    task = select_task()
    input("Press Enter to start the experiment...")

    print("Experiment running. Press Ctrl+C to quit.")

    try:
        for i in range(N_TRIALS):
            # --- REST PHASE ---
            rest_block()

            # --- STIMULI PHASE ---
            stim_duration = random.uniform(*STIM_RANGE)
            print(
                f"Trial {i + 1}/{N_TRIALS} | "
                f"Phase: {STIM_DICT[task]} | Duration: {stim_duration:.2f}s"
            )

            # Start of task: trigger + short beep cue
            outlet.push_sample([task])
            beep()

            # Hold the task period (beep already finished above)
            time.sleep(max(0.0, stim_duration - BEEP_DURATION))

            # End of task: trigger + short beep cue
            outlet.push_sample([REST])
            beep()

        # Final rest block at the end
        rest_block()
        print("\nExperiment complete.")
        pygame.mixer.quit()

    except KeyboardInterrupt:
        print("\nExperiment terminated.")
        pygame.mixer.quit()


if __name__ == "__main__":
    run_trial()

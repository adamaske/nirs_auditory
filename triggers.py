import time
import random
import numpy as np
import pygame
from pylsl import StreamInfo, StreamOutlet

# --- Configuration ---
FS = 44100  
BEEP_FREQ = 1000  
STIM_DICT = {0: "Rest", 1: "Audio", 2: "AudioEnd"}

# Initialize Pygame Mixer
pygame.mixer.init(frequency=FS, size=-16, channels=2)

# --- LSL Setup ---
info = StreamInfo('Trigger', 'Markers', 1, 0, 'int32', 'auditory_trial_001')
outlet = StreamOutlet(info)

def get_beep_sound(duration, frequency=1000, fs=44100):
    """Generates a sine wave and returns a pygame Sound object."""
    t = np.linspace(0, duration, int(fs * duration), False)
    # Smooth edges to prevent 'popping'
    fade = int(fs * 0.05)
    envelope = np.ones_like(t)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    
    # Generate 16-bit PCM audio (reshape to 2D for pygame)
    samples = (np.sin(frequency * t * 2 * np.pi) * 32767 * 0.5 * envelope).astype(np.int16)
    samples = np.column_stack([samples, samples])
    return pygame.sndarray.make_sound(samples)

def run_trial():
    baseline_duration = 15
    print(f"Stream 'Trigger' initialized. Starting {baseline_duration}s baseline...")
    time.sleep(baseline_duration) # Crucial for fNIRS stabilization
    
    print("Experiment running. No popups expected. Press Ctrl+C to quit.")

    try:
        while True:
            # --- REST PHASE ---
            rest_duration = random.uniform(10, 25)
            print(f"Phase: {STIM_DICT[0]} | Duration: {rest_duration:.2f}s")
            outlet.push_sample([0]) 
            time.sleep(rest_duration)

            # --- STIMULI PHASE ---
            stim_duration = random.uniform(2, 12)
            # Create sound object for this specific random duration
            beep_sound = get_beep_sound(stim_duration, BEEP_FREQ, FS)
            
            print(f"Phase: {STIM_DICT[1]} | Duration: {stim_duration:.2f}s")
            
            # Play and trigger simultaneously
            outlet.push_sample([1])
            beep_sound.play()
            
            # Wait for the sound to finish
            time.sleep(stim_duration)
            outlet.push_sample([2])

    except KeyboardInterrupt:
        print("\nExperiment terminated.")
        pygame.mixer.quit()

if __name__ == "__main__":
    run_trial()
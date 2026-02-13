from neuropipeline import fNIRS, fNIRSPreprocessor
from neuropipeline.fnirs import visualizer as nplv

fnirs = fNIRS("C:\\nirs\\data\\2026-01-23\\2026-01-23_002\\2026-01-23_002.snirf")

# Advanced Preprocessing Configuration
pp = fNIRSPreprocessor(fnirs) # Create preprocesssor
pp.set_optical_density(True) # Configure
pp.set_hemoglobin_concentration(True)
pp.set_motion_correction(True)
pp.set_temporal_filtering(True, lowcut=0.01, highcut=0.5, order=5)
pp.set_detrending(True)
pp.set_normalization(False)

pp.print() # Inspect the settings

fnirs.preprocess(pp) # Pass the preprocesser only

fnirs.write_snirf("processed.snirf") # WARNING : Dont overwrite data you want to keep

nplv.set_spectrogram_limits(0.0, 0.2) # The spectrogram will show frequencies from  0 to 0.2 Hz 

nplv.set_marker_dictionary({0:"Rest",      # Display as text rather than indices
                             1:"AudioStart", 
                             2:"AudioEnd"})

nplv.set_spectrum_mode("FFT") # What type of spectrum to show: "FFT" or "PSD"

# NOTE : The wavelet method is computationally intensive
# Try "STFT" first, then "Wavelet" if needed
# "CMT" Complex Morlet Transform  gives better time-frequency resolution, but is even more computationally intensive
nplv.set_spectrogram_method("STFT") 

nplv.open(fnirs)
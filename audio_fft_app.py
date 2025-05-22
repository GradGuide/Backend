
import streamlit as st
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

st.title("Audio Analyzer with FFT & Filtering")

uploaded_file = st.file_uploader("Upload an audio file (WAV only)", type=["wav"])

if uploaded_file is not None:
    signal, sr = librosa.load(uploaded_file, sr=None)
    st.audio(uploaded_file, format='audio/wav')

    st.subheader("1. Waveform")
    fig1, ax1 = plt.subplots()
    librosa.display.waveshow(signal, sr=sr, ax=ax1)
    ax1.set(title='Waveform', xlabel='Time (s)', ylabel='Amplitude')
    st.pyplot(fig1)

    st.subheader("2. Frequency Spectrum (FFT)")
    n = len(signal)
    freq = np.fft.rfftfreq(n, d=1/sr)
    fft_magnitude = np.abs(np.fft.rfft(signal))

    fig2, ax2 = plt.subplots()
    ax2.plot(freq, fft_magnitude)
    ax2.set(title='Frequency Spectrum', xlabel='Frequency (Hz)', ylabel='Magnitude')
    st.pyplot(fig2)

    st.subheader("3. Spectrogram")
    S = librosa.stft(signal)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    fig3, ax3 = plt.subplots()
    img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz', ax=ax3)
    fig3.colorbar(img, ax=ax3, format="%+2.f dB")
    ax3.set(title='Spectrogram')
    st.pyplot(fig3)

    st.subheader("4. Filter Frequency (Bandpass)")
    lowcut = st.slider("Low cutoff (Hz)", 20, 10000, 500)
    highcut = st.slider("High cutoff (Hz)", lowcut+1, 20000, 5000)

    def bandpass_filter(signal, sr, lowcut, highcut):
        fft = np.fft.rfft(signal)
        freq = np.fft.rfftfreq(len(signal), d=1/sr)
        fft[(freq < lowcut) | (freq > highcut)] = 0
        filtered_signal = np.fft.irfft(fft)
        return filtered_signal

    filtered_signal = bandpass_filter(signal, sr, lowcut, highcut)

    fig4, ax4 = plt.subplots()
    librosa.display.waveshow(filtered_signal, sr=sr, ax=ax4)
    ax4.set(title='Filtered Signal', xlabel='Time (s)', ylabel='Amplitude')
    st.pyplot(fig4)

    st.success("Analysis complete.")

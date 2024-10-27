import wave
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

args = None

def parse_arguments():
    global args

    parser = argparse.ArgumentParser(description="Process a file name, unsigned int, and a time unit (min, ms, s) as arguments.")
    
    parser.add_argument('file_name', type=str, help='The name of the file')
    
    parser.add_argument('timestamp', type=check_unsigned_int, help='timestamp (must be >= 0)')

    parser.add_argument('timeFormat', choices=['min', 'ms', 's'], help="The time unit (must be 'min', 'ms', or 's')")
    
    args = parser.parse_args()

def convert_24bit_to_32bit(frames: bytes, nchannels: int):
    data = np.frombuffer(frames, dtype=np.uint8)

    num_samples = len(frames) // 3
    converted = np.zeros(num_samples, dtype=np.int32)

    for i in range(num_samples):
        byte_start = i * 3
        sample = int.from_bytes(data[byte_start:byte_start+3], byteorder='little', signed=True)
        converted[i] = sample

    return np.reshape(converted, (-1, nchannels))

def get_wave_metadata_and_frames(file_path) -> tuple[tuple[int, int, int, int], bytes]:
    with wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        metadata = (
            params.nchannels,
            params.sampwidth,
            params.framerate,
            params.nframes,
        )
        frames = wav_file.readframes(params.nframes)
    return metadata, frames

def plot_wave(file_path):
    file_name: str = os.path.basename(file_path)
    metadata, frames = get_wave_metadata_and_frames(file_path)
    nchannels, sampwidth, framerate, nframes = metadata
    
    # If sampling width is 3 bytes (24-bit) convert it to 32bit value
    if sampwidth == 3:
        wave_data = convert_24bit_to_32bit(frames, nchannels)
    elif sampwidth == 2:
        wave_data = np.frombuffer(frames, dtype=np.int16)
        wave_data = np.reshape(wave_data, (-1, nchannels))
    elif sampwidth == 4:
        wave_data = np.frombuffer(frames, dtype=np.int32)
        wave_data = np.reshape(wave_data, (-1, nchannels))
    else:
        print(f"Sampling width {sampwidth*8}-bit is not supported")
        sys.exit(1)
    
    time = np.linspace(0, len(wave_data) / framerate, num=len(wave_data))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for channel in range(nchannels):
        ax.plot(time, wave_data[:, channel], label=f"Kanalas {channel+1}")

    unit_to_seconds = {'min': 60, 'ms': 0.001, 's': 1}
    time_marker_at = args.timestamp * unit_to_seconds[args.timeFormat]

    if (time_marker_at <= round(nframes / framerate, 3)) and (time_marker_at >= 0):
        plt.axvline(x=time_marker_at, color='b', linestyle='--', label=f"Marker at = {time_marker_at} s")

    ax.legend(loc='upper left')
    
    ax.set_xlabel("Laikas [s]")
    ax.set_ylabel("Amplitudė")
    ax.set_title(f"{file_name}")
    
    metadata_text = f"""\
Failo trukmė: {round(nframes / framerate, 3)} s
Kanalų skaičius: {nchannels}
Diskretizavimo dažnis: {framerate} Hz
Kvantacijos gylis: {sampwidth*8}-bit"""

    inset_ax = fig.add_axes([0.66, 0.72, 0.25, 0.2])  # [left, bottom, width, height]
    inset_ax.text(0.5, 0.5, metadata_text, fontsize=10, ha='center', va='center', transform=inset_ax.transAxes)
    
    inset_ax.set_axis_off()

    plt.show()

def check_unsigned_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"Invalid unsigned int value: {value}. It must be a positive integer.")
    return ivalue

if __name__ == "__main__":
    parse_arguments()
    if not os.path.isfile(args.file_name):
        print(f"Error: File '{args.file_name}' does not exist.")

    plot_wave(args.file_name)

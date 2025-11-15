#!/usr/bin/env python3
"""
FSK (Frequency-Shift Keying) Modulation Program
Converts arbitrary data to sound and back using FSK modulation.
"""

import numpy as np
import wave
import struct
import argparse
import sys
from pathlib import Path


class FSKModem:
    """FSK Modem for encoding and decoding data to/from audio signals."""
    
    def __init__(self, sample_rate=44100, baud_rate=1200, freq_low=1200, freq_high=2400):
        """
        Initialize FSK modem with specified parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)
            baud_rate: Baud rate (bits per second) (default: 1200)
            freq_low: Frequency for bit 0 in Hz (default: 1200)
            freq_high: Frequency for bit 1 in Hz (default: 2400)
        """
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.freq_low = freq_low
        self.freq_high = freq_high
        self.samples_per_bit = sample_rate // baud_rate
        
    def encode_to_audio(self, data):
        """
        Encode binary data to audio signal using FSK modulation.
        
        Args:
            data: bytes object containing data to encode
            
        Returns:
            numpy array of audio samples (float32, -1.0 to 1.0)
        """
        # Convert bytes to bits
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        
        # Generate audio signal
        audio = []
        t = 0
        for bit in bits:
            freq = self.freq_high if bit else self.freq_low
            # Generate one bit worth of samples
            for _ in range(self.samples_per_bit):
                sample = np.sin(2 * np.pi * freq * t / self.sample_rate)
                audio.append(sample)
                t += 1
        
        return np.array(audio, dtype=np.float32)
    
    def decode_from_audio(self, audio_samples):
        """
        Decode FSK modulated audio signal back to binary data.
        
        Args:
            audio_samples: numpy array of audio samples
            
        Returns:
            bytes object containing decoded data
        """
        # Process audio in chunks corresponding to bits
        bits = []
        num_bits = len(audio_samples) // self.samples_per_bit
        
        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            chunk = audio_samples[start:end]
            
            # Detect frequency by comparing correlation with both frequencies
            # Use the actual time indices for this chunk
            t = np.arange(start, end)
            
            # Generate reference signals
            low_ref = np.sin(2 * np.pi * self.freq_low * t / self.sample_rate)
            high_ref = np.sin(2 * np.pi * self.freq_high * t / self.sample_rate)
            
            # Calculate correlations
            corr_low = np.abs(np.sum(chunk * low_ref))
            corr_high = np.abs(np.sum(chunk * high_ref))
            
            # Determine bit value
            bits.append(1 if corr_high > corr_low else 0)
        
        # Convert bits back to bytes
        data = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_bits = bits[i:i+8]
                byte_val = 0
                for j, bit in enumerate(byte_bits):
                    byte_val |= (bit << (7 - j))
                data.append(byte_val)
        
        return bytes(data)
    
    def save_to_wav(self, audio_samples, filename):
        """
        Save audio samples to WAV file.
        
        Args:
            audio_samples: numpy array of audio samples (float32, -1.0 to 1.0)
            filename: output WAV filename
        """
        # Convert to 16-bit PCM
        audio_int16 = (audio_samples * 32767).astype(np.int16)
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    def load_from_wav(self, filename):
        """
        Load audio samples from WAV file.
        
        Args:
            filename: input WAV filename
            
        Returns:
            numpy array of audio samples (float32, -1.0 to 1.0)
        """
        with wave.open(filename, 'rb') as wav_file:
            # Check format
            if wav_file.getnchannels() != 1:
                raise ValueError("Only mono WAV files are supported")
            if wav_file.getsampwidth() != 2:
                raise ValueError("Only 16-bit WAV files are supported")
            
            # Read all frames
            frames = wav_file.readframes(wav_file.getnframes())
            
            # Convert to float32
            audio_int16 = np.frombuffer(frames, dtype=np.int16)
            audio_samples = audio_int16.astype(np.float32) / 32768.0
            
        return audio_samples


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description='FSK Modulation - Convert data to sound and back',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode a file to audio
  %(prog)s encode input.bin output.wav
  
  # Decode audio back to file
  %(prog)s decode input.wav output.bin
  
  # Encode text to audio
  echo "Hello, World!" | %(prog)s encode - output.wav
        """
    )
    
    parser.add_argument('mode', choices=['encode', 'decode'],
                       help='Mode: encode data to audio or decode audio to data')
    parser.add_argument('input', help='Input file (use - for stdin when encoding)')
    parser.add_argument('output', help='Output file')
    parser.add_argument('--sample-rate', type=int, default=44100,
                       help='Audio sample rate in Hz (default: 44100)')
    parser.add_argument('--baud-rate', type=int, default=1200,
                       help='Baud rate in bits/second (default: 1200)')
    parser.add_argument('--freq-low', type=int, default=1200,
                       help='Frequency for bit 0 in Hz (default: 1200)')
    parser.add_argument('--freq-high', type=int, default=2400,
                       help='Frequency for bit 1 in Hz (default: 2400)')
    
    args = parser.parse_args()
    
    # Create modem
    modem = FSKModem(
        sample_rate=args.sample_rate,
        baud_rate=args.baud_rate,
        freq_low=args.freq_low,
        freq_high=args.freq_high
    )
    
    try:
        if args.mode == 'encode':
            # Read input data
            if args.input == '-':
                data = sys.stdin.buffer.read()
            else:
                with open(args.input, 'rb') as f:
                    data = f.read()
            
            if len(data) == 0:
                print("Error: No data to encode", file=sys.stderr)
                return 1
            
            # Encode to audio
            print(f"Encoding {len(data)} bytes to audio...", file=sys.stderr)
            audio = modem.encode_to_audio(data)
            
            # Save to WAV
            modem.save_to_wav(audio, args.output)
            print(f"Saved to {args.output}", file=sys.stderr)
            print(f"Duration: {len(audio) / args.sample_rate:.2f} seconds", file=sys.stderr)
            
        else:  # decode
            # Load audio
            print(f"Loading audio from {args.input}...", file=sys.stderr)
            audio = modem.load_from_wav(args.input)
            
            # Decode to data
            print(f"Decoding audio to data...", file=sys.stderr)
            data = modem.decode_from_audio(audio)
            
            # Save data
            with open(args.output, 'wb') as f:
                f.write(data)
            print(f"Decoded {len(data)} bytes to {args.output}", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

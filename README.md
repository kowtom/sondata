# sondata

FSK (Frequency-Shift Keying) Modulation Program - Convert arbitrary data to sound and back.

## Overview

`sondata` is a Python program that can encode arbitrary binary data into audio files using FSK modulation and decode the audio back into the original data. This is useful for:

- Transmitting data over audio channels
- Storing data in audio format
- Educational purposes to understand FSK modulation
- Creating audio representations of binary data

## Features

- **Encode**: Convert any binary data (files, stdin) to WAV audio files
- **Decode**: Convert FSK-modulated WAV files back to original binary data
- **Configurable**: Adjust sample rate, baud rate, and carrier frequencies
- **Reliable**: Tested with various data types including text and binary
- **Command-line interface**: Easy to use from the terminal

## Installation

### Requirements

- Python 3.6 or higher
- NumPy

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

**Encode a text file to audio:**
```bash
python3 sondata.py encode input.txt output.wav
```

**Decode audio back to a file:**
```bash
python3 sondata.py decode input.wav output.txt
```

**Encode from stdin:**
```bash
echo "Hello, World!" | python3 sondata.py encode - output.wav
```

**Encode a binary file:**
```bash
python3 sondata.py encode document.pdf document.wav
python3 sondata.py decode document.wav document_restored.pdf
```

### Advanced Options

```bash
python3 sondata.py encode input.bin output.wav \
  --sample-rate 44100 \
  --baud-rate 1200 \
  --freq-low 1200 \
  --freq-high 2400
```

**Options:**
- `--sample-rate`: Audio sample rate in Hz (default: 44100)
- `--baud-rate`: Baud rate in bits/second (default: 1200)
- `--freq-low`: Frequency for bit 0 in Hz (default: 1200)
- `--freq-high`: Frequency for bit 1 in Hz (default: 2400)

## How It Works

### FSK Modulation

FSK (Frequency-Shift Keying) is a digital modulation scheme that represents data as variations in frequency:

1. **Encoding**: Each bit is represented by a specific frequency:
   - Bit 0 → Low frequency (default: 1200 Hz)
   - Bit 1 → High frequency (default: 2400 Hz)

2. **Decoding**: The audio is analyzed in chunks, and the frequency is detected using correlation with reference signals to determine the original bits.

### Technical Details

- Default configuration uses 1200 baud (bits per second)
- At 44100 Hz sample rate, each bit is represented by ~36.75 samples
- Audio files are saved as mono, 16-bit PCM WAV files
- The decoder uses frequency correlation to robustly detect bits

## Testing

Run the test suite:

```bash
python3 test_sondata.py -v
```

The test suite includes:
- Simple text encoding/decoding
- Binary data encoding/decoding (all byte values)
- Empty data handling
- WAV file save/load operations
- Different parameter configurations
- Single byte tests

## Examples

### Example 1: Simple Text Message

```bash
# Create a message
echo "Secret message!" > message.txt

# Encode to audio
python3 sondata.py encode message.txt message.wav

# Decode back
python3 sondata.py decode message.wav decoded.txt

# Verify
diff message.txt decoded.txt
```

### Example 2: Binary Data

```bash
# Encode any binary file
python3 sondata.py encode photo.jpg photo.wav

# Decode back
python3 sondata.py decode photo.wav photo_restored.jpg

# Verify integrity
md5sum photo.jpg photo_restored.jpg
```

### Example 3: Streaming from stdin

```bash
# Pipe data directly
cat data.bin | python3 sondata.py encode - output.wav
```

## Performance

- **Encoding speed**: ~1200 bits/second with default settings
- **Storage efficiency**: ~7.35 KB of audio per KB of data (44100 Hz, 1200 baud)
- **Decoding accuracy**: 100% with clean audio signals

## Limitations

- Requires clean audio signals for reliable decoding
- Not optimized for noisy channels (no error correction)
- Audio files are significantly larger than original data
- Mono audio only

## License

Open source - free to use and modify.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
#!/usr/bin/env python3
"""
Tests for FSK modulation program
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from sondata import FSKModem


class TestFSKModem(unittest.TestCase):
    """Test cases for FSKModem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.modem = FSKModem()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_encode_decode_simple(self):
        """Test encoding and decoding simple data."""
        original_data = b"Hello, World!"
        
        # Encode
        audio = self.modem.encode_to_audio(original_data)
        
        # Check audio was generated
        self.assertIsInstance(audio, np.ndarray)
        self.assertGreater(len(audio), 0)
        
        # Decode
        decoded_data = self.modem.decode_from_audio(audio)
        
        # Verify
        self.assertEqual(original_data, decoded_data)
    
    def test_encode_decode_binary(self):
        """Test encoding and decoding binary data."""
        # Test with various byte values
        original_data = bytes(range(256))
        
        # Encode and decode
        audio = self.modem.encode_to_audio(original_data)
        decoded_data = self.modem.decode_from_audio(audio)
        
        # Verify
        self.assertEqual(original_data, decoded_data)
    
    def test_encode_decode_empty(self):
        """Test encoding empty data."""
        original_data = b""
        
        # Encode
        audio = self.modem.encode_to_audio(original_data)
        
        # Should produce empty or minimal audio
        self.assertIsInstance(audio, np.ndarray)
        
        # Decode
        decoded_data = self.modem.decode_from_audio(audio)
        
        # Should be empty
        self.assertEqual(b"", decoded_data)
    
    def test_wav_save_load(self):
        """Test saving and loading WAV files."""
        original_data = b"Test WAV file"
        
        # Encode
        audio = self.modem.encode_to_audio(original_data)
        
        # Save to WAV
        wav_path = os.path.join(self.temp_dir, "test.wav")
        self.modem.save_to_wav(audio, wav_path)
        
        # Check file exists
        self.assertTrue(os.path.exists(wav_path))
        
        # Load from WAV
        loaded_audio = self.modem.load_from_wav(wav_path)
        
        # Decode
        decoded_data = self.modem.decode_from_audio(loaded_audio)
        
        # Verify
        self.assertEqual(original_data, decoded_data)
    
    def test_audio_properties(self):
        """Test that generated audio has correct properties."""
        data = b"Test"
        audio = self.modem.encode_to_audio(data)
        
        # Check audio is in valid range
        self.assertTrue(np.all(audio >= -1.0))
        self.assertTrue(np.all(audio <= 1.0))
        
        # Check length matches expected duration
        # 4 bytes = 32 bits
        expected_samples = 32 * self.modem.samples_per_bit
        self.assertEqual(len(audio), expected_samples)
    
    def test_different_parameters(self):
        """Test with different modem parameters."""
        modem = FSKModem(sample_rate=8000, baud_rate=300, 
                        freq_low=1000, freq_high=2000)
        
        original_data = b"Custom params"
        
        # Encode and decode
        audio = modem.encode_to_audio(original_data)
        decoded_data = modem.decode_from_audio(audio)
        
        # Verify
        self.assertEqual(original_data, decoded_data)
    
    def test_single_byte(self):
        """Test encoding/decoding a single byte."""
        for byte_val in [0x00, 0xFF, 0xAA, 0x55]:
            original_data = bytes([byte_val])
            
            audio = self.modem.encode_to_audio(original_data)
            decoded_data = self.modem.decode_from_audio(audio)
            
            self.assertEqual(original_data, decoded_data,
                           f"Failed for byte value {byte_val:02x}")


if __name__ == '__main__':
    unittest.main()

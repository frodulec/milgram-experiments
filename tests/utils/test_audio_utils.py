import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from io import BytesIO
from src.utils.audio_utils import load_mp3


class TestLoadMp3:
    """Test the load_mp3 function."""
    
    def test_load_mp3_success(self):
        """Test successful loading of an MP3 file."""
        mock_audio_data = b"fake_audio_data"
        
        with patch('os.path.exists', return_value=True), \
             patch('ffmpeg.input') as mock_input, \
             patch('ffmpeg.output') as mock_output:
            
            # Mock the ffmpeg pipeline
            mock_input.return_value.output.return_value.run.return_value = (mock_audio_data, b"")
            
            result = load_mp3("test_audio.mp3")
            
            assert isinstance(result, BytesIO)
            assert result.getvalue() == mock_audio_data
    
    def test_load_mp3_file_not_found(self):
        """Test loading MP3 when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="File test_audio.mp3 does not exist."):
                load_mp3("test_audio.mp3")
    
    def test_load_mp3_ffmpeg_error(self):
        """Test loading MP3 when ffmpeg encounters an error."""
        with patch('os.path.exists', return_value=True), \
             patch('ffmpeg.input') as mock_input, \
             patch('ffmpeg.output') as mock_output:
            
            # Mock ffmpeg error
            from ffmpeg import Error
            mock_input.return_value.output.return_value.run.side_effect = Error(
                cmd=["ffmpeg", "-i", "test.mp3"], 
                stdout=b"", 
                stderr=b"Error: Invalid file format"
            )
            
            with pytest.raises(RuntimeError, match="Error loading MP3 file:"):
                load_mp3("test_audio.mp3")
    
    def test_load_mp3_general_exception(self):
        """Test loading MP3 when a general exception occurs."""
        with patch('os.path.exists', return_value=True), \
             patch('ffmpeg.input') as mock_input, \
             patch('ffmpeg.output') as mock_output:
            
            # Mock general exception
            mock_input.return_value.output.return_value.run.side_effect = Exception("General error")
            
            with pytest.raises(RuntimeError, match="Error loading MP3 file: General error"):
                load_mp3("test_audio.mp3")
    
    def test_load_mp3_with_path_object(self):
        """Test loading MP3 with a Path object."""
        mock_audio_data = b"fake_audio_data"
        
        with patch('os.path.exists', return_value=True), \
             patch('ffmpeg.input') as mock_input, \
             patch('ffmpeg.output') as mock_output:
            
            # Mock the ffmpeg pipeline
            mock_input.return_value.output.return_value.run.return_value = (mock_audio_data, b"")
            
            from pathlib import Path
            result = load_mp3(Path("test_audio.mp3"))
            
            assert isinstance(result, BytesIO)
            assert result.getvalue() == mock_audio_data
    
    def test_load_mp3_ffmpeg_pipeline_verification(self):
        """Test that the ffmpeg pipeline is called correctly."""
        mock_audio_data = b"fake_audio_data"
        
        with patch('os.path.exists', return_value=True), \
             patch('ffmpeg.input') as mock_input, \
             patch('ffmpeg.output') as mock_output:
            
            # Mock the ffmpeg pipeline
            mock_input.return_value.output.return_value.run.return_value = (mock_audio_data, b"")
            
            load_mp3("test_audio.mp3")
            
            # Verify ffmpeg was called correctly
            mock_input.assert_called_once_with("test_audio.mp3")
            mock_input.return_value.output.assert_called_once_with('pipe:', format='mp3', codec='copy')
            mock_input.return_value.output.return_value.run.assert_called_once_with(
                capture_stdout=True, capture_stderr=True
            )

import os
import pytest
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys

# Set up test environment before importing record module
os.environ.setdefault('RTSP_URL', 'rtsp://test.example.com/stream')
os.environ.setdefault('CAM_NAME', 'test_cam')
os.environ.setdefault('OUT_DIR', '/test/recordings')
os.environ.setdefault('SEGMENT_SECONDS', '60')
os.environ.setdefault('FFMPEG_LOGLEVEL', 'warning')
os.environ.setdefault('RETENTION_DAYS', '30')

# Import the module to test
import record


class TestDateDirName:
    """Tests for date_dir_name function"""
    
    def test_date_dir_name_format(self):
        """Test that date_dir_name returns correct MM-DD-YYYY format"""
        result = record.date_dir_name()
        # Should match MM-DD-YYYY format
        assert len(result) == 10
        parts = result.split('-')
        assert len(parts) == 3
        assert len(parts[0]) == 2  # Month
        assert len(parts[1]) == 2  # Day
        assert len(parts[2]) == 4  # Year
        # Verify it's a valid date
        datetime.strptime(result, "%m-%d-%Y")
    
    def test_date_dir_name_matches_current_date(self):
        """Test that date_dir_name returns today's date"""
        result = record.date_dir_name()
        expected = datetime.now().strftime("%m-%d-%Y")
        assert result == expected


class TestBuildOutputPattern:
    """Tests for build_output_pattern function"""
    
    @patch('record.ensure_dir')
    def test_build_output_pattern_with_current_date(self, mock_ensure_dir):
        """Test build_output_pattern with explicit current_date"""
        test_date = "01-20-2026"
        result = record.build_output_pattern(test_date)
        
        # Use the actual CAM_NAME and OUT_DIR from the module
        expected_path = f"{record.OUT_DIR}/{record.CAM_NAME}/{test_date}/{record.CAM_NAME}_%Y%m%d_%H%M%S.mkv"
        assert result == expected_path
        mock_ensure_dir.assert_called_once()
    
    @patch('record.ensure_dir')
    @patch('record.date_dir_name')
    def test_build_output_pattern_without_current_date(self, mock_date_dir, mock_ensure_dir):
        """Test build_output_pattern without current_date (uses date_dir_name)"""
        mock_date_dir.return_value = "12-25-2025"
        result = record.build_output_pattern()
        
        expected_path = f"{record.OUT_DIR}/{record.CAM_NAME}/12-25-2025/{record.CAM_NAME}_%Y%m%d_%H%M%S.mkv"
        assert result == expected_path
        mock_date_dir.assert_called_once()
        mock_ensure_dir.assert_called_once()
    
    @patch('record.ensure_dir')
    def test_build_output_pattern_creates_directory(self, mock_ensure_dir):
        """Test that build_output_pattern creates the directory"""
        test_date = "01-19-2026"
        record.build_output_pattern(test_date)
        
        # Verify ensure_dir was called with the correct path
        mock_ensure_dir.assert_called_once()
        call_args = mock_ensure_dir.call_args[0][0]
        assert test_date in str(call_args)
        assert record.CAM_NAME in str(call_args)


class TestFfmpegCmd:
    """Tests for ffmpeg_cmd function"""
    
    @patch('record.build_output_pattern')
    def test_ffmpeg_cmd_structure(self, mock_build_pattern):
        """Test that ffmpeg_cmd returns correct command structure"""
        mock_build_pattern.return_value = "/test/output_%Y%m%d_%H%M%S.mkv"
        cmd = record.ffmpeg_cmd()
        
        assert cmd[0] == "ffmpeg"
        assert "-hide_banner" in cmd
        assert "-loglevel" in cmd
        assert cmd[cmd.index("-loglevel") + 1] == record.LOGLEVEL
        assert "-rtsp_transport" in cmd
        assert cmd[cmd.index("-rtsp_transport") + 1] == "tcp"
        assert "-i" in cmd
        assert cmd[cmd.index("-i") + 1] == record.RTSP_URL
        assert "-c" in cmd
        assert cmd[cmd.index("-c") + 1] == "copy"
        assert "-f" in cmd
        assert cmd[cmd.index("-f") + 1] == "segment"
        assert "-segment_time" in cmd
        assert cmd[cmd.index("-segment_time") + 1] == str(record.SEGMENT_SECONDS)
        assert "-segment_format" in cmd
        assert cmd[cmd.index("-segment_format") + 1] == "mkv"
        assert "-strftime" in cmd
        assert cmd[cmd.index("-strftime") + 1] == "1"
        assert cmd[-1] == "/test/output_%Y%m%d_%H%M%S.mkv"
    
    @patch('record.build_output_pattern')
    def test_ffmpeg_cmd_with_current_date(self, mock_build_pattern):
        """Test ffmpeg_cmd passes current_date to build_output_pattern"""
        test_date = "01-20-2026"
        record.ffmpeg_cmd(test_date)
        
        mock_build_pattern.assert_called_once_with(test_date)
    
    @patch('record.build_output_pattern')
    def test_ffmpeg_cmd_without_current_date(self, mock_build_pattern):
        """Test ffmpeg_cmd calls build_output_pattern without date when not provided"""
        record.ffmpeg_cmd()
        
        mock_build_pattern.assert_called_once_with(None)
    
    @patch('record.build_output_pattern')
    def test_ffmpeg_cmd_contains_required_flags(self, mock_build_pattern):
        """Test that ffmpeg_cmd contains all required flags"""
        mock_build_pattern.return_value = "/test/output_%Y%m%d_%H%M%S.mkv"
        cmd = record.ffmpeg_cmd()
        cmd_str = " ".join(cmd)
        
        # Check for important flags
        assert "-rtsp_transport tcp" in cmd_str
        assert "-fflags +genpts+igndts+discardcorrupt" in cmd_str
        assert "-use_wallclock_as_timestamps 1" in cmd_str
        assert "-c copy" in cmd_str
        assert "-reset_timestamps 1" in cmd_str


class TestEnsureDir:
    """Tests for ensure_dir function"""
    
    @patch('pathlib.Path.mkdir')
    def test_ensure_dir_creates_directory(self, mock_mkdir):
        """Test that ensure_dir creates directory with parents"""
        test_path = Path("/test/path/to/dir")
        record.ensure_dir(test_path)
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestCleanupOldRecordings:
    """Tests for retention cleanup logic"""

    def test_cleanup_old_recordings_removes_directories_older_than_cutoff(self, tmp_path):
        """Test that dated directories older than the retention cutoff are removed"""
        with patch.object(record, 'OUT_DIR', str(tmp_path)), \
             patch.object(record, 'CAM_NAME', 'test_cam'), \
             patch.object(record, 'RETENTION_DAYS', 30):
            root = Path(record.OUT_DIR) / record.CAM_NAME
            old_dir = root / "02-15-2026"
            cutoff_dir = root / "02-16-2026"
            recent_dir = root / "03-01-2026"

            old_dir.mkdir(parents=True)
            cutoff_dir.mkdir(parents=True)
            recent_dir.mkdir(parents=True)

            record.cleanup_old_recordings(now=datetime(2026, 3, 18, 12, 0, 0))

            assert not old_dir.exists()
            assert cutoff_dir.exists()
            assert recent_dir.exists()

    def test_cleanup_old_recordings_ignores_invalid_directory_names(self, tmp_path):
        """Test that non-date directories are ignored"""
        with patch.object(record, 'OUT_DIR', str(tmp_path)), \
             patch.object(record, 'CAM_NAME', 'test_cam'), \
             patch.object(record, 'RETENTION_DAYS', 30):
            root = Path(record.OUT_DIR) / record.CAM_NAME
            valid_dir = root / "02-15-2026"
            invalid_dir = root / "manual_exports"

            valid_dir.mkdir(parents=True)
            invalid_dir.mkdir(parents=True)

            record.cleanup_old_recordings(now=datetime(2026, 3, 18, 12, 0, 0))

            assert not valid_dir.exists()
            assert invalid_dir.exists()

    def test_cleanup_old_recordings_noops_when_retention_disabled(self, tmp_path):
        """Test that cleanup is skipped when retention is disabled"""
        with patch.object(record, 'OUT_DIR', str(tmp_path)), \
             patch.object(record, 'CAM_NAME', 'test_cam'), \
             patch.object(record, 'RETENTION_DAYS', 0):
            root = Path(record.OUT_DIR) / record.CAM_NAME
            old_dir = root / "01-01-2026"
            old_dir.mkdir(parents=True)

            record.cleanup_old_recordings(now=datetime(2026, 3, 18, 12, 0, 0))

            assert old_dir.exists()


class TestDateChangeDetection:
    """Tests for date change detection logic"""
    
    @patch('record.date_dir_name')
    def test_date_change_detection_logic(self, mock_date_dir):
        """Test the logic for detecting date changes"""
        # Simulate checking dates
        mock_date_dir.side_effect = ["01-19-2026", "01-20-2026"]
        
        date1 = record.date_dir_name()
        date2 = record.date_dir_name()
        
        assert date1 == "01-19-2026"
        assert date2 == "01-20-2026"
        assert date1 != date2  # Date changed


class TestIntegration:
    """Integration tests"""
    
    @patch('record.ensure_dir')
    def test_date_dir_name_integration_with_build_output_pattern(self, mock_ensure_dir):
        """Test that date_dir_name and build_output_pattern work together"""
        # Get current date
        current_date = record.date_dir_name()
        
        # Build pattern with that date
        pattern = record.build_output_pattern(current_date)
        
        # Verify the pattern contains the date
        assert current_date in pattern
        assert record.CAM_NAME in pattern
        assert record.OUT_DIR in pattern
    
    @patch('record.ensure_dir')
    def test_ffmpeg_cmd_integration(self, mock_ensure_dir):
        """Test that ffmpeg_cmd integrates with build_output_pattern"""
        test_date = "01-20-2026"
        cmd = record.ffmpeg_cmd(test_date)
        
        # Verify the output pattern in the command contains the date
        output_pattern = cmd[-1]
        assert test_date in output_pattern
        assert record.CAM_NAME in output_pattern
    
    @patch('record.ensure_dir')
    def test_full_workflow(self, mock_ensure_dir):
        """Test the full workflow from date to ffmpeg command"""
        # Get a date
        test_date = "01-20-2026"
        
        # Build output pattern
        pattern = record.build_output_pattern(test_date)
        
        # Build ffmpeg command
        cmd = record.ffmpeg_cmd(test_date)
        
        # Verify everything is connected
        assert pattern == cmd[-1]
        assert test_date in pattern
        assert record.CAM_NAME in pattern


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

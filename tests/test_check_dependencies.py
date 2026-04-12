"""
Unit tests for the dependency checker script.

Tests verify that the dependency checker correctly identifies:
- Python version requirements
- Required library installations
- WebDriver availability
- Error message formatting
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Import the checker
sys.path.insert(0, '.')
from check_dependencies import DependencyChecker


class TestDependencyChecker(unittest.TestCase):
    """Test cases for DependencyChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = DependencyChecker()
    
    def test_check_python_version_success(self):
        """Test Python version check passes for 3.8+."""
        # Current Python should be 3.8+ if tests are running
        result = self.checker.check_python_version()
        
        self.assertTrue(result)
        self.assertEqual(len(self.checker.errors), 0)
        self.assertTrue(any("Python version" in msg for msg in self.checker.success_messages))
    
    def test_check_python_version_failure(self):
        """Test Python version check fails for < 3.8."""
        # Create a mock version_info with proper attributes
        mock_version = MagicMock()
        mock_version.major = 3
        mock_version.minor = 7
        mock_version.micro = 0
        
        with patch('sys.version_info', mock_version):
            result = self.checker.check_python_version()
        
        self.assertFalse(result)
        self.assertTrue(len(self.checker.errors) > 0)
        self.assertTrue(any("Python 3.8+ is required" in error for error in self.checker.errors))
    
    @patch('builtins.__import__')
    def test_check_required_libraries_all_installed(self, mock_import):
        """Test library check passes when all libraries are installed."""
        # Mock all required libraries as installed
        mock_module = MagicMock()
        mock_module.__version__ = "1.0.0"
        mock_import.return_value = mock_module
        
        result = self.checker.check_required_libraries()
        
        self.assertTrue(result)
        self.assertEqual(len(self.checker.errors), 0)
    
    @patch('builtins.__import__')
    def test_check_required_libraries_missing(self, mock_import):
        """Test library check fails when libraries are missing."""
        # Mock ImportError for missing library
        mock_import.side_effect = ImportError("No module named 'bs4'")
        
        result = self.checker.check_required_libraries()
        
        self.assertFalse(result)
        self.assertTrue(len(self.checker.errors) > 0)
        self.assertTrue(any("Missing library" in error for error in self.checker.errors))
    
    @patch('builtins.__import__')
    def test_check_testing_libraries_optional(self, mock_import):
        """Test testing library check generates warnings, not errors."""
        # Mock ImportError for missing testing library
        mock_import.side_effect = ImportError("No module named 'pytest'")
        
        result = self.checker.check_testing_libraries()
        
        self.assertFalse(result)
        self.assertTrue(len(self.checker.warnings) > 0)
        self.assertEqual(len(self.checker.errors), 0)  # Should be warnings, not errors
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_webdriver_chrome_available(self, mock_run, mock_which):
        """Test WebDriver check succeeds when ChromeDriver is available."""
        # Mock ChromeDriver found
        mock_which.side_effect = lambda x: "/usr/bin/chromedriver" if x == "chromedriver" else None
        
        # Mock successful version check
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ChromeDriver 120.0.6099.109"
        mock_run.return_value = mock_result
        
        chrome_ok, firefox_ok = self.checker.check_webdriver()
        
        self.assertTrue(chrome_ok)
        self.assertFalse(firefox_ok)
        self.assertEqual(len(self.checker.errors), 0)
        self.assertTrue(any("ChromeDriver" in msg for msg in self.checker.success_messages))
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_webdriver_firefox_available(self, mock_run, mock_which):
        """Test WebDriver check succeeds when GeckoDriver is available."""
        # Mock GeckoDriver found
        mock_which.side_effect = lambda x: "/usr/bin/geckodriver" if x == "geckodriver" else None
        
        # Mock successful version check
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "geckodriver 0.33.0"
        mock_run.return_value = mock_result
        
        chrome_ok, firefox_ok = self.checker.check_webdriver()
        
        self.assertFalse(chrome_ok)
        self.assertTrue(firefox_ok)
        self.assertEqual(len(self.checker.errors), 0)
        self.assertTrue(any("GeckoDriver" in msg for msg in self.checker.success_messages))
    
    @patch('shutil.which')
    def test_check_webdriver_none_available(self, mock_which):
        """Test WebDriver check fails when no WebDriver is available."""
        # Mock no WebDriver found
        mock_which.return_value = None
        
        chrome_ok, firefox_ok = self.checker.check_webdriver()
        
        self.assertFalse(chrome_ok)
        self.assertFalse(firefox_ok)
        self.assertTrue(len(self.checker.errors) > 0)
        self.assertTrue(any("No WebDriver found" in error for error in self.checker.errors))
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_webdriver_both_available(self, mock_run, mock_which):
        """Test WebDriver check succeeds when both drivers are available."""
        # Mock both drivers found
        mock_which.side_effect = lambda x: f"/usr/bin/{x}"
        
        # Mock successful version checks
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ChromeDriver 120.0.6099.109"
        mock_run.return_value = mock_result
        
        chrome_ok, firefox_ok = self.checker.check_webdriver()
        
        self.assertTrue(chrome_ok or firefox_ok)  # At least one should be available
        self.assertEqual(len(self.checker.errors), 0)
    
    def test_error_messages_contain_installation_instructions(self):
        """Test that error messages include helpful installation instructions."""
        # Trigger some errors
        with patch('builtins.__import__', side_effect=ImportError()):
            self.checker.check_required_libraries()
        
        with patch('shutil.which', return_value=None):
            self.checker.check_webdriver()
        
        # Verify error messages contain installation instructions
        all_errors = '\n'.join(self.checker.errors)
        self.assertTrue("pip install" in all_errors or "Download from" in all_errors)
    
    def test_success_messages_include_versions(self):
        """Test that success messages include version information."""
        self.checker.check_python_version()
        
        # Should have at least one success message with version info
        self.assertTrue(len(self.checker.success_messages) > 0)
        self.assertTrue(any("version" in msg.lower() for msg in self.checker.success_messages))
    
    @patch.object(DependencyChecker, 'check_python_version', return_value=True)
    @patch.object(DependencyChecker, 'check_required_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_testing_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_webdriver', return_value=(True, False))
    def test_run_all_checks_success(self, mock_webdriver, mock_testing, mock_libraries, mock_python):
        """Test run_all_checks returns True when all critical checks pass."""
        result = self.checker.run_all_checks()
        
        self.assertTrue(result)
        mock_python.assert_called_once()
        mock_libraries.assert_called_once()
        mock_testing.assert_called_once()
        mock_webdriver.assert_called_once()
    
    @patch.object(DependencyChecker, 'check_python_version', return_value=False)
    @patch.object(DependencyChecker, 'check_required_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_testing_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_webdriver', return_value=(True, False))
    def test_run_all_checks_failure_python(self, mock_webdriver, mock_testing, mock_libraries, mock_python):
        """Test run_all_checks returns False when Python version check fails."""
        result = self.checker.run_all_checks()
        
        self.assertFalse(result)
    
    @patch.object(DependencyChecker, 'check_python_version', return_value=True)
    @patch.object(DependencyChecker, 'check_required_libraries', return_value=False)
    @patch.object(DependencyChecker, 'check_testing_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_webdriver', return_value=(True, False))
    def test_run_all_checks_failure_libraries(self, mock_webdriver, mock_testing, mock_libraries, mock_python):
        """Test run_all_checks returns False when library check fails."""
        result = self.checker.run_all_checks()
        
        self.assertFalse(result)
    
    @patch.object(DependencyChecker, 'check_python_version', return_value=True)
    @patch.object(DependencyChecker, 'check_required_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_testing_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_webdriver', return_value=(False, False))
    def test_run_all_checks_failure_webdriver(self, mock_webdriver, mock_testing, mock_libraries, mock_python):
        """Test run_all_checks returns False when WebDriver check fails."""
        result = self.checker.run_all_checks()
        
        self.assertFalse(result)
    
    @patch.object(DependencyChecker, 'check_python_version', return_value=True)
    @patch.object(DependencyChecker, 'check_required_libraries', return_value=True)
    @patch.object(DependencyChecker, 'check_testing_libraries', return_value=False)
    @patch.object(DependencyChecker, 'check_webdriver', return_value=(True, False))
    def test_run_all_checks_success_despite_testing_failure(self, mock_webdriver, mock_testing, mock_libraries, mock_python):
        """Test run_all_checks returns True even when testing libraries are missing."""
        # Testing libraries are optional, so should still succeed
        result = self.checker.run_all_checks()
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

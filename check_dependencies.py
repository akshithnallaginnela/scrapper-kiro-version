#!/usr/bin/env python3
"""
Dependency Verification Script for Organic Products Web Scraper

This script verifies that all required dependencies are installed and properly
configured before running the scraper.

Requirements validated:
- Python version (3.8+)
- Required Python libraries
- WebDriver availability (ChromeDriver/GeckoDriver)
"""

import sys
import subprocess
import shutil
from typing import List, Tuple


class DependencyChecker:
    """Checks system dependencies for the web scraper."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success_messages: List[str] = []
    
    def check_python_version(self) -> bool:
        """
        Verify Python version is 3.8 or higher.
        
        Returns:
            bool: True if version requirement is met, False otherwise
        """
        print("Checking Python version...")
        
        version_info = sys.version_info
        current_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            self.errors.append(
                f"Python 3.8+ is required. Current version: {current_version}\n"
                f"  → Please upgrade Python: https://www.python.org/downloads/"
            )
            return False
        
        self.success_messages.append(f"✓ Python version {current_version} (requirement: 3.8+)")
        return True
    
    def check_required_libraries(self) -> bool:
        """
        Verify all required Python libraries are installed.
        
        Returns:
            bool: True if all libraries are installed, False otherwise
        """
        print("Checking required Python libraries...")
        
        required_libraries = [
            ("beautifulsoup4", "bs4", "4.9.0"),
            ("selenium", "selenium", "4.0.0"),
            ("requests", "requests", "2.25.0"),
            ("pyyaml", "yaml", "5.4.0"),
            ("lxml", "lxml", "4.6.0"),
        ]
        
        all_installed = True
        
        for package_name, import_name, min_version in required_libraries:
            try:
                module = __import__(import_name)
                version = getattr(module, "__version__", "unknown")
                self.success_messages.append(f"✓ {package_name} {version} (requirement: {min_version}+)")
            except ImportError:
                self.errors.append(
                    f"Missing library: {package_name}\n"
                    f"  → Install with: pip install {package_name}>={min_version}"
                )
                all_installed = False
        
        return all_installed
    
    def check_testing_libraries(self) -> bool:
        """
        Verify testing libraries are installed (optional but recommended).
        
        Returns:
            bool: True if all testing libraries are installed, False otherwise
        """
        print("Checking testing libraries (optional)...")
        
        testing_libraries = [
            ("pytest", "pytest", "7.0.0"),
            ("hypothesis", "hypothesis", "6.0.0"),
            ("pytest-cov", "pytest_cov", "3.0.0"),
        ]
        
        all_installed = True
        
        for package_name, import_name, min_version in testing_libraries:
            try:
                module = __import__(import_name)
                version = getattr(module, "__version__", "unknown")
                self.success_messages.append(f"✓ {package_name} {version} (requirement: {min_version}+)")
            except ImportError:
                self.warnings.append(
                    f"Testing library not installed: {package_name}\n"
                    f"  → Install with: pip install {package_name}>={min_version}\n"
                    f"  → Or install all testing dependencies: pip install -r requirements.txt"
                )
                all_installed = False
        
        return all_installed
    
    def check_webdriver(self) -> Tuple[bool, bool]:
        """
        Verify WebDriver availability (ChromeDriver or GeckoDriver).
        
        Returns:
            Tuple[bool, bool]: (chrome_available, firefox_available)
        """
        print("Checking WebDriver availability...")
        
        chrome_available = False
        firefox_available = False
        
        # Check ChromeDriver
        chromedriver_path = shutil.which("chromedriver")
        if chromedriver_path:
            try:
                result = subprocess.run(
                    ["chromedriver", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split()[1] if result.stdout else "unknown"
                    self.success_messages.append(f"✓ ChromeDriver {version} found at {chromedriver_path}")
                    chrome_available = True
            except (subprocess.TimeoutExpired, FileNotFoundError, IndexError):
                pass
        
        # Check GeckoDriver
        geckodriver_path = shutil.which("geckodriver")
        if geckodriver_path:
            try:
                result = subprocess.run(
                    ["geckodriver", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version_line = result.stdout.strip().split("\n")[0]
                    version = version_line.split()[1] if len(version_line.split()) > 1 else "unknown"
                    self.success_messages.append(f"✓ GeckoDriver {version} found at {geckodriver_path}")
                    firefox_available = True
            except (subprocess.TimeoutExpired, FileNotFoundError, IndexError):
                pass
        
        # Report errors if neither is available
        if not chrome_available and not firefox_available:
            self.errors.append(
                "No WebDriver found. At least one is required (ChromeDriver or GeckoDriver).\n"
                "  → For ChromeDriver:\n"
                "    - Download from: https://chromedriver.chromium.org/\n"
                "    - Ensure it matches your Chrome browser version\n"
                "    - Add to system PATH\n"
                "  → For GeckoDriver:\n"
                "    - Download from: https://github.com/mozilla/geckodriver/releases\n"
                "    - Add to system PATH\n"
                "  → Verify installation: chromedriver --version (or geckodriver --version)"
            )
        elif not chrome_available:
            self.warnings.append(
                "ChromeDriver not found. Firefox/GeckoDriver will be used.\n"
                "  → To use Chrome, install ChromeDriver: https://chromedriver.chromium.org/"
            )
        elif not firefox_available:
            self.warnings.append(
                "GeckoDriver not found. Chrome/ChromeDriver will be used.\n"
                "  → To use Firefox, install GeckoDriver: https://github.com/mozilla/geckodriver/releases"
            )
        
        return chrome_available, firefox_available
    
    def run_all_checks(self) -> bool:
        """
        Run all dependency checks.
        
        Returns:
            bool: True if all critical dependencies are met, False otherwise
        """
        print("=" * 70)
        print("Organic Products Web Scraper - Dependency Verification")
        print("=" * 70)
        print()
        
        # Run all checks
        python_ok = self.check_python_version()
        print()
        
        libraries_ok = self.check_required_libraries()
        print()
        
        testing_ok = self.check_testing_libraries()
        print()
        
        chrome_ok, firefox_ok = self.check_webdriver()
        webdriver_ok = chrome_ok or firefox_ok
        print()
        
        # Display results
        print("=" * 70)
        print("VERIFICATION RESULTS")
        print("=" * 70)
        print()
        
        # Success messages
        if self.success_messages:
            print("✓ SUCCESS:")
            for msg in self.success_messages:
                print(f"  {msg}")
            print()
        
        # Warnings
        if self.warnings:
            print("⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # Errors
        if self.errors:
            print("✗ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # Final verdict
        all_critical_ok = python_ok and libraries_ok and webdriver_ok
        
        if all_critical_ok:
            print("=" * 70)
            print("✓ All critical dependencies are satisfied!")
            print("  You can now run the scraper with: python -m src.main")
            print("=" * 70)
            return True
        else:
            print("=" * 70)
            print("✗ Some critical dependencies are missing.")
            print("  Please install the missing dependencies and run this script again.")
            print("=" * 70)
            return False


def main():
    """Main entry point for dependency checking."""
    checker = DependencyChecker()
    success = checker.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

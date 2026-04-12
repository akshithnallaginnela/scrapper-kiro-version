# Contributing to Organic Products Web Scraper

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs from `scraper.log`

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature already exists
- Describe the feature clearly
- Explain why it would be useful
- Provide examples if possible

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation
4. **Run tests**
   ```bash
   pytest
   pytest --cov=src --cov-report=html
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/scrapper-kiro-version.git
cd scrapper-kiro-version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest
```

## 🎨 Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add type hints where appropriate

Format code with Black:
```bash
black src/ tests/
```

Lint with flake8:
```bash
flake8 src/ tests/
```

## ✅ Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage (currently 91%)
- Use pytest for unit tests
- Use Hypothesis for property-based tests
- Mock external dependencies

Test structure:
```python
def test_feature_name():
    # Arrange
    setup_test_data()
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_value
```

## 📝 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update configuration guides if needed

## 🔍 Code Review Process

All submissions require review. We use GitHub pull requests for this purpose:

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged

## 🏷️ Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add new feature
fix: Fix bug in component
docs: Update documentation
test: Add tests for feature
refactor: Refactor code
style: Format code
chore: Update dependencies
```

## 📦 Adding Dependencies

If you need to add a new dependency:

1. Add it to `requirements.txt`
2. Explain why it's needed in your PR
3. Ensure it's compatible with Python 3.8+

## 🐛 Debugging

- Enable debug logging: `log_level: "DEBUG"` in config
- Check `scraper.log` for detailed logs
- Use test mode for faster debugging
- Add print statements or use debugger

## 🚀 Release Process

Releases are managed by maintainers:

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create git tag
4. Push to GitHub
5. Create GitHub release

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

- Open an issue for questions
- Check existing issues and documentation first
- Be respectful and constructive

## 🙏 Thank You!

Your contributions make this project better for everyone!

---

**Built with ❤️ using Kiro AI**

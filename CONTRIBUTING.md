# Contributing to Metisara

Thank you for your interest in contributing to Metisara! 🏛️

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a virtual environment and install dependencies
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/metisara.git
cd metisara

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Copy example configuration
cp examples/metisara.conf.example metisara.conf
cp .env.example .env
# Edit .env with your JIRA API token
```

## Making Changes

### Code Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to new functions and classes
- Keep line length under 100 characters

### Testing
- Write tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for good test coverage

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src/metisara

# Run linting
flake8 src/
black --check src/
mypy src/
```

### Commit Messages
Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep first line under 50 characters
- Use present tense
- Reference issues when applicable

Examples:
```
Add support for custom field mapping
Fix epic linking for large projects
Update README with installation instructions
```

## Types of Contributions

### Bug Reports
When reporting bugs, please include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information (OS, Python version)
- Log files (use `./metis --report-issue` to generate diagnostic package)

### Feature Requests
For new features:
- Describe the use case
- Explain why it would be valuable
- Consider backward compatibility
- Provide examples if possible

### Code Contributions
- Start with small, focused changes
- Discuss large changes in an issue first
- Include tests for new functionality
- Update documentation as needed

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the guidelines above
3. **Test thoroughly** - run full test suite
4. **Update documentation** if needed
5. **Submit pull request** with clear description

### PR Requirements
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear

## Code Review Process

- Maintainers will review PRs within a few days
- Address any feedback or requested changes
- Once approved, maintainers will merge

## Security

If you discover security vulnerabilities:
- **DO NOT** open a public issue
- Email the maintainers directly
- Include full details and steps to reproduce

## Questions?

- Open an issue for questions
- Check existing issues and documentation first
- Be respectful and constructive

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Respect different viewpoints and experiences

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information
- Other unprofessional conduct

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks for first-time contributors

Thank you for helping make Metisara better! 🏛️
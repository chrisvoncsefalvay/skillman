# Contributing to skillman

Thank you for your interest in contributing to skillman! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to contribute

### Reporting bugs

1. Check if the bug has already been reported
2. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include:
   - OS and Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and tracebacks

### Suggesting features

1. Check if the feature has been requested
2. Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Describe:
   - The problem it solves
   - Use cases
   - Proposed solution
   - Alternative approaches

### Contributing code

#### Setup development environment

1. **Fork and clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/skillman.git
   cd skillman
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

#### Making changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, readable code
   - Add type hints for new functions
   - Follow the existing code style
   - Add docstrings for public functions

3. **Write tests**:
   ```bash
   pytest tests/
   ```

4. **Run quality checks**:
   ```bash
   # Format code
   black skillman

   # Lint
   flake8 skillman

   # Type check
   mypy skillman

   # Test coverage
   pytest --cov=skillman
   ```

5. **All checks must pass before submitting PR**

#### Code style

- **Python style**: Black (configured in pyproject.toml)
- **Type hints**: Required for new functions
- **Documentation**: Docstrings for all public functions
- **Testing**: Aim for >80% coverage

Example:

```python
def example_function(name: str, count: int = 1) -> List[str]:
    """Process items.

    Args:
        name: The name to process
        count: Number of times to process

    Returns:
        List of processed items
    """
    # Implementation
    return []
```

#### Commit messages

Use clear, descriptive commit messages:

```
Add feature X to handle Y

- Describe what changed
- Explain why (if not obvious)
- Reference related issues

Fixes #123
```

#### Submitting pull requests

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**:
   - Use the [PR template](.github/pull_request_template.md)
   - Link related issues
   - Describe changes clearly
   - List testing done

3. **Respond to feedback**:
   - Address review comments
   - Rerun tests
   - Update PR as needed

4. **Merge**:
   - Maintainer will merge when approved
   - Branch is auto-deleted after merge

## Release process

### For maintainers

1. **Update version**:
   ```bash
   # Update pyproject.toml
   version = "0.4.0"

   # Update skillman/__init__.py
   __version__ = "0.4.0"
   ```

2. **Create tag**:
   ```bash
   git tag v0.4.0 -m "Release 0.4.0"
   git push origin v0.4.0
   ```

3. **Workflows run automatically**:
   - Tests
   - Packaging
   - PyPI publishing

4. **Verify release**:
   - Check GitHub Releases
   - Check PyPI
   - Test installation

See [CICD.md](CICD.md) for detailed CI/CD information.

## Dev tools

### Testing

```bash
# Run all tests
pytest -v

# Run specific test
pytest tests/test_cli.py::test_add -v

# With coverage
pytest --cov=skillman --cov-report=html
```

### Debugging

```bash
# Verbose logging
skillman -vv init

# Debug mode
import pdb; pdb.set_trace()
```

### Profiling

```bash
# Time command execution
time skillman add anthropics/skills/canvas-design

# Memory profiling (install: pip install memory-profiler)
python -m memory_profiler skillman/__main__.py
```

## Project structure

```
skillman/
├── __init__.py          # Version and package info
├── cli.py               # Command-line interface (2.2 KB)
├── models.py            # Data models
├── github.py            # GitHub integration
├── config.py            # Configuration management
├── installer.py         # Installation engine
└── utils.py             # Utilities

tests/                   # Unit tests (coming soon)
.github/
├── workflows/           # GitHub Actions workflows
├── ISSUE_TEMPLATE/      # Issue templates
└── pull_request_template.md

pyproject.toml           # Package configuration
README.md                # User documentation
PUBLISHING.md            # Publishing guide
DEPLOYMENT.md            # Deployment guide
CICD.md                  # CI/CD documentation
```

## Areas for contribution

### High priority

- [ ] Add more testing (unit and integration)
- [ ] Improve error messages
- [ ] Add logging and statsig
- [ ] Documentation improvements

### Medium Priority

- [ ] Performance optimization
- [ ] Additional skill sources (not just GitHub)
- [ ] Dry-run improvements
- [ ] Configuration enhancements

### Nice to Have

- [ ] Shell completions (bash, zsh, fish)
- [ ] Interactive mode
- [ ] Plugin system
- [ ] Web UI
- [ ] API server

## Getting Help

- **Issues**: Ask questions in GitHub issues
- **Discussions**: Use GitHub Discussions (if enabled)
- **Email**: Check repository for contact info

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes
- Future contributors list in documentation

## Questions?

Feel free to ask! Open an issue with your question tagged as `question`.

Thank you for contributing to skillman!

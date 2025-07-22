# Contributing to KrishiAI

We're excited you're interested in contributing to KrishiAI! This guide will help you get started with the development process.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Testing](#testing)
- [Code Style](#code-style)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
   ```bash
   git clone https://github.com/your-username/KrishiAI.git
   cd KrishiAI
   ```
3. **Set up the development environment** (see below)
4. **Create a new branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your own API keys

4. **Run the development server**
   ```bash
   python app.py
   ```

## Making Changes

1. **Follow the coding style** (see below)
2. **Write tests** for new features or bug fixes
3. **Update documentation** as needed
4. **Commit your changes** with clear, descriptive messages
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

1. Ensure all tests pass
2. Update the README.md with details of changes if needed
3. Submit a pull request to the `main` branch
4. Address any code review feedback

## Reporting Issues

When creating an issue, please include:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant screenshots or error messages
- Your environment (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! Please open an issue with:
- A clear description of the feature
- The problem it solves
- Any alternative solutions you've considered

## Testing

Run the test suite with:
```bash
python -m pytest
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use 4 spaces for indentation
- Keep lines under 100 characters
- Include docstrings for all public functions and classes
- Write clear, concise commit messages

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

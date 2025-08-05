<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

---
applyTo: "*.py"
---

# Project general coding standards
This is a basic Python project. Use best practices for Python development, including virtual environments and requirements.txt for dependencies.

## Coding style
- Follow PEP 8 for Python code style.
- Use Google Python style guide for docstrings
    - Refer to section 3.8 of [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for detailed guidelines on writing docstrings.

## Typing
- Use type hints for function signatures and class attributes

---
applyTo: "scratchpad.py"
---
# Scratchpad for quick experiments
This file is intended for quick code snippets and experiments. It is not part of the main project structure and should not be used for production code.
- Use this file for testing small code snippets or trying out new ideas without affecting the main codebase.
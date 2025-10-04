# Contributing to Kartavya SIEM NLP Assistant

Thank you for your interest in contributing to the Kartavya SIEM NLP Assistant project! 🎉

## 📚 Documentation

Before contributing, please review our comprehensive documentation:
- **[Documentation Hub](../docs/README.md)** - Complete guide to the project
- **[Project Structure](../docs/PROJECT_STRUCTURE.md)** - Understand the codebase
- **[Architecture](../docs/ARCHITECTURE_DIAGRAM.md)** - System design

## 🤝 How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow our coding standards (see below)
- Add tests for new features
- Update documentation if needed

### 4. Commit & Push
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Go to the repository on GitHub
- Click "New Pull Request"
- Describe your changes clearly

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add support for Splunk SIEM integration
fix: resolve intent classification accuracy issue
docs: update API documentation with new endpoints
```

## 💻 Code Style Guidelines

### Python Code Style
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

```python
# Good
def extract_entities(query: str) -> Dict[str, List[str]]:
    """Extract entities from natural language query."""
    entities = {}
    # Implementation
    return entities

# Avoid
def ee(q):
    e = {}
    return e
```

### File Organization
- Group related functions together
- Add docstrings to all functions/classes
- Keep files under 500 lines when possible

### Documentation
- Update README.md for major changes
- Add/update docstrings for new functions
- Update relevant docs in `docs/` folder

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parser.py

# Run with coverage
pytest --cov=. tests/
```

### Writing Tests
- Write tests for all new features
- Maintain minimum 80% code coverage
- Use meaningful test names

```python
def test_intent_classifier_identifies_search_events():
    """Test that intent classifier correctly identifies search events."""
    classifier = IntentClassifier()
    intent, confidence = classifier.classify_intent("Show failed logins")
    assert intent == QueryIntent.SEARCH_EVENTS
    assert confidence > 0.7
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description** - Clear description of the issue
2. **Steps to Reproduce** - Exact steps to reproduce the bug
3. **Expected Behavior** - What you expected to happen
4. **Actual Behavior** - What actually happened
5. **Environment** - OS, Python version, dependencies
6. **Screenshots/Logs** - If applicable

**Template:**
```markdown
**Bug Description:**
Intent classifier returns wrong intent for query "show alerts"

**Steps to Reproduce:**
1. Start the backend
2. Send query: "show alerts"
3. Observe intent classification

**Expected:** ALERT_QUERY
**Actual:** SEARCH_EVENTS

**Environment:**
- OS: Windows 11
- Python: 3.10.5
- Branch: main
```

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. Check existing issues first
2. Open a new issue with label `enhancement`
3. Describe the feature clearly
4. Explain the use case
5. Provide examples if possible

## 📂 Project Structure

Key directories:
```
backend/          - FastAPI backend
  nlp/           - NLP processing
  response_formatter/ - Response formatting
ui_dashboard/    - Streamlit frontend
siem_connector/  - SIEM integrations
docs/            - Documentation
tests/           - Test suite
```

See [PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md) for detailed breakdown.

## 🔍 Code Review Process

1. **Automated Checks** - CI/CD runs tests automatically
2. **Review** - Maintainer reviews code
3. **Discussion** - Address feedback/questions
4. **Approval** - Code approved by maintainer
5. **Merge** - PR merged into main branch

## 🎯 Areas for Contribution

We especially welcome contributions in:

- 🧠 **NLP Improvements** - Better intent classification, entity extraction
- 🔌 **SIEM Integrations** - Support for Splunk, QRadar, etc.
- 📊 **Visualizations** - New chart types, dashboards
- 📝 **Documentation** - Tutorials, examples, guides
- 🧪 **Testing** - More test coverage
- 🐛 **Bug Fixes** - Any bug you find!

## 📞 Getting Help

- **Documentation Issues**: Open issue with `docs` label
- **Code Questions**: Open discussion on GitHub
- **General Questions**: Check [FAQ](../docs/FAQ.md)

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in project README

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain professionalism

## 🎓 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Elasticsearch Guide](https://www.elastic.co/guide/)
- [Our Documentation](../docs/README.md)

## 📅 Development Cycle

- **Sprint Duration**: 2 weeks
- **Release Cycle**: Monthly
- **Version Format**: Semantic Versioning (MAJOR.MINOR.PATCH)

---

**Thank you for contributing to Kartavya SIEM NLP Assistant!** 🚀

For more information, see our [Documentation](../docs/README.md).

---

**Team Kartavya** | **SIH 2025** | **Problem Statement: SIH25173**

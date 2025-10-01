# Contributing to Spiral Codex Unified

Thank you for your interest in contributing to Spiral Codex Unified! This document provides guidelines and best practices for contributing to this project.

## Table of Contents

- [Commit Message Standards](#commit-message-standards)
- [Conventional Commits Format](#conventional-commits-format)
- [Commit Message Examples](#commit-message-examples)
- [Using the Commit Template](#using-the-commit-template)
- [Pre-commit Hook Setup](#pre-commit-hook-setup)
- [Best Practices](#best-practices)
- [Development Workflow](#development-workflow)

## Commit Message Standards

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for all commit messages. This leads to more readable messages that are easy to follow when looking through the project history and enables automated changelog generation.

### Why Conventional Commits?

- **Automated versioning**: Semantic versioning can be automatically determined
- **Changelog generation**: Automatically generate CHANGELOGs
- **Clear history**: Easy to understand what changed and why
- **Better collaboration**: Consistent format helps team communication
- **Tool compatibility**: Works well with all Git tools and CI/CD systems

## Conventional Commits Format

### Basic Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

The type must be one of the following:

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `feat` | A new feature | Adding new functionality |
| `fix` | A bug fix | Fixing a broken feature |
| `docs` | Documentation only changes | README, comments, docstrings |
| `style` | Code style changes (formatting, missing semi-colons, etc) | Black, Ruff formatting |
| `refactor` | Code change that neither fixes a bug nor adds a feature | Restructuring code |
| `perf` | Performance improvements | Optimizing algorithms |
| `test` | Adding or correcting tests | Unit tests, integration tests |
| `build` | Changes to build system or dependencies | requirements.txt, setup.py |
| `ci` | Changes to CI configuration | GitHub Actions, workflows |
| `chore` | Other changes that don't modify src or test files | Updating .gitignore |
| `revert` | Reverts a previous commit | Undoing a change |

### Scope (Optional)

The scope provides additional contextual information and is contained within parentheses:

- `agent`: Changes to agent-related code
- `workflow`: Changes to workflow logic
- `config`: Configuration changes
- `api`: API-related changes
- `ui`: User interface changes
- `core`: Core functionality changes

### Subject

The subject contains a succinct description of the change:

- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No period (.) at the end
- Limit to 72 characters or less

### Body (Optional)

The body should include the motivation for the change and contrast this with previous behavior:

- Use the imperative, present tense
- Wrap at 72 characters
- Explain what and why vs. how

### Footer (Optional)

The footer should contain:

- **Breaking changes**: Start with `BREAKING CHANGE:` followed by description
- **Issue references**: `Closes #123`, `Fixes #456`, `Resolves #789`

## Commit Message Examples

### ✅ Good Examples

```
feat(agent): add multi-agent coordination support

Implement MAC protocol for coordinating multiple agents in parallel.
This enables better resource utilization and faster task completion.

Closes #42
```

```
fix(workflow): resolve CI syntax errors

Correct YAML indentation in GitHub Actions workflow file to ensure
proper pipeline execution.
```

```
docs: update README with installation instructions

Add detailed setup guide including virtual environment creation,
dependency installation, and configuration steps.
```

```
refactor(core): simplify agent registry initialization

Remove redundant initialization logic and consolidate registry
setup into a single method for better maintainability.
```

```
ci: implement complete CI/CD pipeline with quality gates

Add comprehensive CI/CD workflow including:
- Code linting (Black, Ruff)
- Type checking (mypy)
- Unit tests (pytest)
- Coverage reporting

Establishes quality gates for all pull requests.
```

### ❌ Bad Examples

```
❌ Add stuff
   Problem: Too vague, no type, no description

❌ Fixed bug
   Problem: No type prefix, unclear what was fixed

❌ 🚦 Full CI/CD with lint, type checks, tests, coverage
   Problem: Emoji usage, no conventional prefix, too long

❌ Updated files
   Problem: No type, unclear what was updated and why

❌ WIP: working on feature
   Problem: Not descriptive, WIP commits should be squashed before merging

❌ feat: Added new feature for agents and also fixed some bugs and updated docs
   Problem: Multiple changes in one commit, should be separate commits
```

## Using the Commit Template

We provide a commit message template to help you write properly formatted commit messages.

### Setup (One-time)

Configure Git to use the template globally for this repository:

```bash
git config commit.template .gitmessage
```

Or globally for all repositories:

```bash
git config --global commit.template ~/.gitmessage
```

### Usage

When you run `git commit` (without the `-m` flag), your editor will open with the template pre-filled:

```bash
git commit
```

Simply fill in the placeholders and remove the comment lines.

## Pre-commit Hook Setup

We provide a pre-commit hook that automatically validates your commit messages against the conventional commits format.

### Automatic Setup

The hook is already configured in `.git/hooks/commit-msg`. If you've cloned the repository, it should work automatically.

### Manual Setup (if needed)

If the hook isn't working, ensure it's executable:

```bash
chmod +x .git/hooks/commit-msg
```

### Testing the Hook

Try committing with an invalid message:

```bash
git commit -m "bad message"
```

You should see an error message explaining the correct format.

Try committing with a valid message:

```bash
git commit -m "feat(test): add validation test"
```

This should succeed.

## Best Practices

### 1. Atomic Commits

Each commit should represent a single logical change:

✅ **Good**: Separate commits for separate concerns
```
feat(agent): add coordination protocol
test(agent): add coordination protocol tests
docs(agent): document coordination protocol
```

❌ **Bad**: Multiple unrelated changes in one commit
```
feat: add coordination protocol, fix bug in workflow, update README
```

### 2. Test Before Committing

- Run tests locally before pushing
- Use tools like `act` to test GitHub Actions workflows locally
- Avoid multiple consecutive "fix" commits

### 3. Meaningful Commit Messages

Write commit messages that explain:
- **What** changed
- **Why** it changed
- **How** it affects the system (if not obvious)

### 4. Avoid Emojis

While visually appealing, emojis:
- May not render in all Git tools
- Are not part of the conventional commits standard
- Can cause issues in automated tools

### 5. Squash Before Merging

Before merging to main:
- Squash "WIP" commits
- Squash consecutive fix commits
- Squash duplicate commits
- Keep meaningful, atomic commits

### 6. Breaking Changes

If your change breaks backward compatibility:

```
feat(api)!: change agent initialization signature

BREAKING CHANGE: Agent constructor now requires 'config' parameter.
Migration guide: Pass AgentConfig() as first parameter to Agent().
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Write code, tests, and documentation.

### 3. Commit with Conventional Format

```bash
git commit -m "feat(scope): add new feature"
```

Or use the template:

```bash
git commit
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

### 5. Address Review Comments

Make changes and commit with appropriate messages:

```bash
git commit -m "fix(scope): address review comments"
```

### 6. Squash if Needed

Before merging, squash WIP or fix commits:

```bash
git rebase -i main
```

## Questions?

If you have questions about contributing, please:

1. Check existing issues and pull requests
2. Review this contributing guide
3. Open a new issue with your question

Thank you for contributing to Spiral Codex Unified! 🎉

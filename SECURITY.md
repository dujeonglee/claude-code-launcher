# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security seriously at Claude Code Launcher. If you discover a security vulnerability, please report it to us responsibly.

### How to Report

Please do NOT create a public GitHub issue for security vulnerabilities. Instead, please report them via email to the maintainers:

- Primary: claudeLauncherMaintainers@example.com (placeholder)

Include the following information in your report:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Any mitigating factors
5. Your name/handle (optional, for credit)

### Response Timeline

We aim to respond to security reports within 48 hours and provide a more detailed response within 72 hours. We will keep you informed of our progress.

## Security Measures

### Currently Implemented

1. **No hardcoded secrets**: API keys are stored in user configuration files, not in source code
2. **HTTPS downloads**: Claude Code binaries are downloaded over HTTPS from Google Cloud Storage
3. **SHA256 checksum verification**: Downloaded binaries are verified against known checksums
4. **No shell injection**: Script generation uses proper quoting and escaping
5. **File permissions**: Binary files are set with appropriate permissions (executable only by owner)
6. **Config permissions**: Configuration files are created with user-only permissions

### Security Best Practices

- Never commit API keys or sensitive data
- Run linters (`pylint`) before committing
- Use type hints to catch potential issues early
- Review security checklist before releases

## Known Limitations

1. **Terminal launching**: The application uses platform-specific terminal launching which may have platform-specific security considerations
2. **Configuration storage**: Configuration is stored in the user's home directory in plain text YAML format

## Security Announcements

Security announcements will be posted to the project's GitHub repository and included in the CHANGELOG.md file.

## Security Credits

We thank the following contributors for security research:

- [Your Name Here] - [Description of discovery]

## Security Tools

The project uses the following security tools:

- `pylint` for static analysis
- `mypy` for type checking
- Regular code reviews

## Privacy

This project does not collect or transmit any user data. All configuration is stored locally on the user's machine.

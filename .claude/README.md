# Claude Agent & Skill Framework

This directory contains the agent and skill configurations that define Claude Code's development workflow for this project.

## Agents

Agents are specialized AI assistants that each handle a specific part of the software development lifecycle.

### Auditor Agent

**File**: `.claude/agents/auditor.md`

Purpose: Security and architecture audit specialist.

**When to use**:
- Security reviews
- Architecture analysis
- Dependency checks
- Vulnerability assessments

**Key capabilities**:
- OWASP Top 10 vulnerability scanning
- Architecture quality assessment
- Circular dependency detection
- Security checklist compliance

### Implementer Agent

**File**: `.claude/agents/implementer.md`

Purpose: Production code implementation specialist.

**When to use**:
- Writing new code
- Creating modules/classes
- Refactoring existing code
- Feature implementation

**Key capabilities**:
- SOLID design principles
- Incremental delivery
- Error handling patterns
- Language-specific guidelines (Python, TypeScript, C++, Rust, Go)

### Verifier Agent

**File**: `.claude/agents/verifier.md`

Purpose: Software verification and testing specialist.

**When to use**:
- Running tests
- Checking coverage
- Static analysis
- Debugging test failures

**Key capabilities**:
- Test execution across frameworks (pytest, Jest, cargo test, GoogleTest)
- Coverage measurement and gap analysis
- Static analysis tool integration
- Test quality assessment

### Documenter Agent

**File**: `.claude/agents/documenter.md`

Purpose: Documentation specialist.

**When to use**:
- Creating/updating READMEs
- Writing API docs
- Creating ADRs
- Writing changelogs

**Key capabilities**:
- Documentation standards and templates
- README structure guidelines
- Docstring standards (Google style, TSDoc, Doxygen)
- Changelog format (Keep a Changelog)

### SDLC Orchestrator Agent

**File**: `.claude/agents/sdlc-orchestrator.md`

Purpose: End-to-end software delivery orchestrator.

**When to use**:
- Feature delivery
- Bug fixes
- Complete lifecycle changes

**Key capabilities**:
- 4-phase delivery pipeline (Implement → Verify → Audit → Document)
- Quality gates between phases
- Error handling and rollback
- Delivery reporting

## Skills

Skills contain methodologies, templates, and best practices that agents use.

### Audit Skill

**Directory**: `.claude/skills/audit/`

**Files**:
- `SKILL.md` - Main audit methodology
- `SECURITY_CHECKLIST.md` - OWASP Top 10 checklist
- `ARCHITECTURE_REVIEW.md` - Architecture review guide

**Key contents**:
- Quick grep patterns for vulnerabilities
- Architecture quality metrics
- Severity definitions and reporting templates

### Implement Skill

**Directory**: `.claude/skills/implement/`

**File**: `SKILL.md`

**Key contents**:
- SOLID design principles
- Error handling patterns (Python, TypeScript, C++, Rust)
- Scaffolding templates
- Common patterns (DI, Builder, Strategy)

### Verify Skill

**Directory**: `.claude/skills/verify/`

**File**: `SKILL.md`

**Key contents**:
- Testing pyramid (70% unit, 20% integration, 10% E2E)
- Test structure (Arrange-Act-Assert)
- Framework quick references
- Coverage targets

### Document Skill

**Directory**: `.claude/skills/document/`

**File**: `SKILL.md`

**Key contents**:
- Documentation type reference
- README structure standard
- Docstring standards
- Changelog format

## Workflow

### Feature Delivery Pipeline

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   IMPLEMENT   │────▶│    VERIFY     │────▶│     AUDIT     │────▶│   DOCUMENT    │
│ (Implementer) │     │  (Verifier)   │     │   (Auditor)   │     │ (Documenter)  │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │                     │
  Gate: Code            Gate: Tests          Gate: No             Gate: Docs
  compiles &            pass, coverage       critical/high        complete &
  follows spec          ≥ threshold          findings             accurate
```

### Triggering Agents

Agents are triggered by specific keywords in your request:

| Agent | Triggers |
|-------|----------|
| Implementer | implement, build, create, write code, add feature, refactor |
| Verifier | test, verify, check, coverage, lint, static analysis |
| Auditor | audit, security review, architecture review, vulnerability |
| Documenter | document, docs, README, API docs, ADR, changelog |
| SDLC Orchestrator | deliver feature, full lifecycle, end to end |

## Directory Structure

```
.clause/
├── agents/               # Agent definitions
│   ├── auditor.md
│   ├── implementer.md
│   ├── verifier.md
│   ├── documenter.md
│   └── sdlc-orchestrator.md
└── skills/               # Skill methodologies
    ├── audit/
    │   ├── SKILL.md
    │   ├── SECURITY_CHECKLIST.md
    │   └── ARCHITECTURE_REVIEW.md
    ├── implement/
    │   └── SKILL.md
    ├── verify/
    │   └── SKILL.md
    └── document/
        └── SKILL.md
```

## Customization

### Adding New Agents

1. Create `agents/<name>.md`
2. Define purpose, triggers, and capabilities
3. Reference relevant skills

### Adding New Skills

1. Create `skills/<name>/SKILL.md`
2. Include methodology, templates, and examples
3. Reference from agents that need it

## Best Practices

1. **Quality Gates**: Never skip quality gates in the SDLC pipeline
2. **Evidence-Based**: All audit findings must reference specific code locations
3. **Actionable**: Every finding must include remediation guidance
4. **Progressive**: Implement in small, testable increments
5. **Document First**: Update docs before marking features complete

# Architecture Review Guide

Structured approach to evaluating software architecture quality, modularity,
and maintainability.

## Layered Architecture Check

Verify that the codebase follows proper layering:

```
┌─────────────────────────────┐
│  Presentation / API Layer   │  ← Routes, controllers, CLI, UI
├─────────────────────────────┤
│  Application / Service Layer│  ← Use cases, orchestration, DTOs
├─────────────────────────────┤
│  Domain / Business Layer    │  ← Entities, value objects, rules
├─────────────────────────────┤
│  Infrastructure / Data Layer│  ← DB, external APIs, file I/O
└─────────────────────────────┘
```

**Rule**: Dependencies only flow downward. Upper layers depend on lower layers.
Lower layers NEVER import from upper layers.

### How to check:

```bash
# Find potential layering violations (Python example)
# If "routes" or "controllers" appear in imports of "models" or "repositories"
grep -rn "from.*routes\|from.*controllers\|from.*views" \
  --include="*.py" src/models/ src/repositories/ src/domain/
```

## Circular Dependency Detection

### Manual approach (small codebases):

```bash
# List all imports grouped by file
grep -rn "^from \|^import " --include="*.py" src/ | \
  sed 's/:.*from /: imports /; s/:.*import /: imports /' | \
  sort

# Look for A→B and B→A patterns in the output
```

### Algorithmic approach (Tarjan's SCC):

For larger codebases, use dependency analysis tools:

```bash
# Python
pip install pydeps
pydeps src/ --no-show --no-output --cluster

# Or use custom analysis:
python -c "
import ast, sys, os
from collections import defaultdict

# Build import graph
graph = defaultdict(set)
for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            module = path.replace('/', '.').replace('.py', '')
            try:
                tree = ast.parse(open(path).read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        graph[module].add(node.module)
            except: pass

# Find cycles (simplified)
visited = set()
path_set = set()
cycles = []

def dfs(node, path):
    visited.add(node)
    path_set.add(node)
    for neighbor in graph.get(node, []):
        if neighbor in path_set:
            cycle_start = path.index(neighbor) if neighbor in path else -1
            if cycle_start >= 0:
                cycles.append(path[cycle_start:] + [neighbor])
        elif neighbor not in visited:
            dfs(neighbor, path + [neighbor])
    path_set.discard(node)

for node in graph:
    if node not in visited:
        dfs(node, [node])

for c in cycles:
    print(' -> '.join(c))
"
```

## Module Quality Metrics

### God Module Detection

A "God Module" has too many responsibilities. Indicators:

| Metric | God Module Threshold |
|--------|---------------------|
| Lines of code | > 500 |
| Number of classes | > 5 |
| Number of public functions | > 20 |
| Number of imports | > 15 |
| Fan-in (dependents) | > 10 |
| Fan-out (dependencies) | > 10 |

### Coupling Analysis

```bash
# Count how many files import each module (fan-in)
grep -rn "from.*import\|^import " --include="*.py" src/ | \
  awk -F'import ' '{print $2}' | \
  awk -F'[ ,.]' '{print $1}' | \
  sort | uniq -c | sort -rn | head -20

# Count how many modules each file imports (fan-out)
grep -rn "^from \|^import " --include="*.py" src/ | \
  awk -F: '{print $1}' | \
  sort | uniq -c | sort -rn | head -20
```

### Cohesion Assessment

Signs of **low cohesion** (bad):
- Class has methods that don't use any shared state
- File contains unrelated classes/functions
- Module name is vague ("utils", "helpers", "misc", "common")
- Functions in same module operate on completely different data types

Signs of **high cohesion** (good):
- All methods in a class work with the same data
- Module has a single, clear responsibility
- Functions share common data types and concepts
- Module name precisely describes its purpose

## Refactoring Recommendations Matrix

| Finding | Severity | Recommended Action |
|---------|----------|-------------------|
| Circular dependency (2 modules) | HIGH | Extract shared types to new module |
| Circular dependency (3+ modules) | HIGH | Apply dependency inversion principle |
| God module (> 500 LOC) | MEDIUM | Split by responsibility |
| High fan-out (> 10 deps) | MEDIUM | Introduce facade or mediator |
| Layering violation | HIGH | Move code to correct layer |
| Duplicate code (3+ instances) | MEDIUM | Extract to shared function/module |
| Deep nesting (> 4 levels) | LOW | Extract inner blocks to functions |
| Long parameter list (> 5) | LOW | Introduce parameter object |

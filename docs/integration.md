# Integration Guide

How to use capability entries with AI agents and automation.

## Agent Pre-flight Checks

Before an agent claims it can perform a task, it should validate requirements:

```python
def can_execute(capability: dict, context: dict) -> tuple[bool, list[str]]:
    """Check if capability requirements are satisfied."""
    blockers = []

    for source in capability['requires'].get('sources_of_truth', []):
        if not validate_source(source, context):
            blockers.append(f"Source unavailable: {source['name']}")

    for access in capability['requires'].get('access', []):
        if not check_access(access, context):
            blockers.append(f"Access missing: {access}")

    for dep in capability['requires'].get('dependencies', []):
        dep_cap = load_capability(dep)
        can_dep, dep_blockers = can_execute(dep_cap, context)
        if not can_dep:
            blockers.append(f"Dependency blocked: {dep}")
            blockers.extend(dep_blockers)

    return len(blockers) == 0, blockers
```

## Communicating Limitations

When a capability has known gaps relevant to the current task, surface them:

```python
def get_relevant_warnings(capability: dict, task: str) -> list[str]:
    """Return known gaps that might affect this task."""
    warnings = []

    for gap in capability['confidence'].get('known_gaps', []):
        if is_relevant_to_task(gap, task):
            warnings.append(f"⚠️ {gap}")

    return warnings
```

Example agent response:

> I can help debug this API issue, but note:
> - ⚠️ Dev environment logs are not in the aggregator—I can only query production
> - ⚠️ Log retention is 30 days—older events won't be available

## Capability Composition

Some tasks require multiple capabilities. Use the dependency graph:

```yaml
# debugging-workflow.yaml
id: api-debugging-workflow
name: API Debugging Workflow
domain: observability
version: 1.0.0

action:
  description: End-to-end API debugging from error to root cause

requires:
  dependencies:
    - rest-api-client        # Reproduce the issue
    - log-aggregator-query   # Find error logs
    - database-query         # Check data state
```

## Loading Capabilities

### From Local Files

```python
import yaml
from pathlib import Path

def load_capabilities(catalog_path: Path) -> dict:
    """Load all capabilities from a catalog directory."""
    capabilities = {}

    for yaml_file in catalog_path.glob("**/*.yaml"):
        if yaml_file.name == "capability.schema.yaml":
            continue
        with open(yaml_file) as f:
            cap = yaml.safe_load(f)
            capabilities[cap['id']] = cap

    return capabilities
```

### From Git Repository

```bash
# Clone and use as submodule
git submodule add https://github.com/your-org/capabilities.git .capabilities

# Or fetch specific files
curl -sL https://raw.githubusercontent.com/your-org/capabilities/main/capabilities/my-cap.yaml
```

## Validation

Validate capability entries against the schema:

```bash
# Using yajsv (YAML JSON Schema Validator)
yajsv -s schema/capability.schema.yaml capabilities/**/*.yaml

# Using Python jsonschema
python -c "
import yaml
import jsonschema

with open('schema/capability.schema.yaml') as f:
    schema = yaml.safe_load(f)

with open('capabilities/my-cap.yaml') as f:
    cap = yaml.safe_load(f)

jsonschema.validate(cap, schema)
print('Valid!')
"
```

## CI/CD Integration

Add capability validation to your pipeline:

```yaml
# .github/workflows/validate.yml
name: Validate Capabilities
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install validators
        run: |
          pip install pyyaml jsonschema

      - name: Validate all capabilities
        run: |
          python scripts/validate_capabilities.py
```

## Runtime Context

Pass runtime context to capability checks:

```python
runtime_context = {
    'vpn_connected': check_vpn_status(),
    'env': os.getenv('ENVIRONMENT', 'development'),
    'credentials': {
        'api_token': os.getenv('API_TOKEN') is not None,
        'db_access': can_connect_to_db(),
    },
    'tools': {
        'apicli': shutil.which('apicli') is not None,
        'jq': shutil.which('jq') is not None,
    }
}

can_run, blockers = can_execute(capability, runtime_context)
```

## Best Practices

1. **Fail fast**: Check requirements before starting work
2. **Be specific**: Tell users exactly what's missing, not just "can't do that"
3. **Suggest alternatives**: If capability A is blocked, maybe capability B works
4. **Cache validations**: Don't re-check static requirements repeatedly
5. **Update on failure**: If a capability fails unexpectedly, update `failure_modes`

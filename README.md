# Capability Catalog

A schema and framework for documenting grounded, composable agent capabilities.

## The Problem

Agents claim capabilities without context. "I can debug your API" means nothing without knowing:
- Which environment?
- What log access?
- Current schema version?
- VPN state?
- Required credentials?

The gap between **claimed capability** and **grounded capability** is where agents become unreliable.

## The Solution

This framework provides a schema for documenting capabilities as contracts—not marketing copy. Each entry specifies exactly what's required to execute, what can go wrong, and what honest limitations exist.

**A capability = skill + environment context + truth dependencies**

## Quick Start

### 1. Create your capabilities directory

```bash
git clone https://github.com/jcaldwell-labs/capability-catalog.git
cd capability-catalog

# Create your own capabilities (keep these private or public as needed)
mkdir -p capabilities/your-domain
```

### 2. Write a capability entry

```yaml
# capabilities/your-domain/my-capability.yaml
id: my-api-client
name: My API Client
domain: development-tooling
version: 1.0.0

action:
  description: Execute CRUD operations against MyService API
  trigger: When testing API endpoints or debugging integration issues
  examples:
    - "mycli get /users/123"
    - "mycli post /orders --data '{...}'"

requires:
  sources_of_truth:
    - name: API endpoint configuration
      location: ~/.mycli/config.yaml
      freshness: static
      validation: "mycli config check"
  access:
    - VPN connected to internal network
    - Valid API token in environment
  environment:
    - mycli v2.0+ installed

produces:
  outputs:
    - format: JSON
      destination: stdout
      consumers: [debugging, test validation]

confidence:
  maturity: stable
  known_gaps:
    - No retry logic on transient failures
    - Pagination not supported for large result sets
  failure_modes:
    - VPN disconnect returns "connection refused" (no helpful message)
    - Expired token returns generic 401

metadata:
  author: your-name
  created: 2025-01-15
  tags: [api, testing, cli]
```

### 3. Use capabilities for pre-flight checks

Before an agent claims "I can help with that", it checks:

```yaml
requires:
  access:
    - VPN connected           # ✅ Can verify
    - Valid API token         # ❓ Need to check
  known_gaps:
    - No pagination support   # ⚠️ May hit this on large queries
```

Now the agent knows what to verify before proceeding.

## Schema

See [schema/capability.schema.yaml](schema/capability.schema.yaml) for the full schema definition.

### Core Sections

| Section | Purpose |
|---------|---------|
| `action` | What this capability does and when it triggers |
| `requires` | Sources of truth, access, dependencies, environment, context |
| `produces` | Outputs and side effects |
| `confidence` | Maturity level, known gaps, failure modes |
| `metadata` | Author, dates, tags, related resources |

### Maturity Levels

| Level | Meaning |
|-------|---------|
| `experimental` | Proof of concept. May not work. |
| `developing` | Works but rough edges. |
| `stable` | Reliable for normal use. |
| `battle-tested` | Proven under production pressure. |

### Freshness Levels

| Level | Meaning |
|-------|---------|
| `real-time` | Must be live (database connection) |
| `minutes` | Stale after minutes (cache) |
| `hours` | Stale after hours |
| `daily` | Updated daily |
| `static` | Doesn't change (CLI binary, config) |

## Examples

See [examples/](examples/) for complete capability entries:

- `examples/api-testing/rest-client.yaml` — Generic REST API testing
- `examples/observability/log-query.yaml` — Log aggregation queries
- `examples/context-management/session-tracking.yaml` — Development session tracking

## Documentation

- [Authoring Guide](docs/authoring.md) — How to write good capability entries
- [Integration Guide](docs/integration.md) — Using capabilities with AI agents
- [Schema Reference](docs/schema-reference.md) — Full schema documentation

## Philosophy

### Honesty Over Marketing

This exists because **honesty about limitations is more valuable than optimistic claims**.

An agent that says "I can't query dev logs because they're not in the log aggregator" is more useful than one that confidently runs queries and returns nothing.

### Contracts, Not Descriptions

Each capability entry is a contract:
- If `requires` is satisfied, the capability should work
- If it doesn't work, `failure_modes` should explain why
- `known_gaps` are documented upfront, not discovered through frustration

### Composability

Capabilities can depend on other capabilities. This makes the dependency graph explicit:

```yaml
dependencies:
  - database-query      # Need to get IDs first
  - log-aggregator-query  # Then correlate with logs
```

## Use Cases

1. **Agent Self-Assessment**: Before claiming a capability, verify requirements
2. **Onboarding Documentation**: New team members understand what's actually available
3. **Incident Response**: Know exactly what tools work in which environments
4. **Capability Planning**: Identify gaps in your tooling coverage

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

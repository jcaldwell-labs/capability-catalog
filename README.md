# Capability Catalog

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Schema Version](https://img.shields.io/badge/schema-1.0.0-blue.svg)](schema/capability.schema.yaml)

> Skills tell agents what they know. Capabilities tell them what they can actually do *right now*.

A schema and framework for documenting grounded, composable agent capabilities.

## Why Capability Catalog?

| Challenge | Skills Alone | With Capabilities |
|-----------|--------------|-------------------|
| **Context awareness** | "I can query logs" | "I can query logs, but dev-cf doesn't log to the aggregator" |
| **Pre-flight validation** | Discover failures mid-task | Check requirements before starting |
| **Honest limitations** | Optimistic claims | Documented `known_gaps` and `failure_modes` |
| **Environment changes** | Same claim everywhere | Grounded to current VPN, credentials, access |
| **Debugging failures** | Generic errors | Context-aware diagnostics from failure modes |

**The gap between claimed capability and grounded capability is where agents become unreliable.** This framework closes that gap.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jcaldwell-labs/capability-catalog.git
cd capability-catalog
```

### 2. Run Pre-flight Check

Validate that capability requirements are satisfied before execution:

```bash
python scripts/preflight.py examples/observability/log-query.yaml
```

Output:
```
============================================================
Pre-flight Check: Log Aggregator Query
ID: log-aggregator-query | Maturity: stable
============================================================

Sources of Truth:
  ✓ Log aggregator access
      Accessible via SSO

Access Requirements:
  ⚠ Log aggregator account with read permissions
      Manual verification needed

Known Gaps (review before proceeding):
  ⚠ Dev-tenant-A does NOT log to aggregator
  ⚠ Log retention limits historical queries

Summary:
  Passed: 1 | Failed: 0 | Unknown: 1

⚠ CAUTION: 1 requirement(s) need manual verification
```

### 3. Validate Your Capabilities

Ensure capability files conform to the schema:

```bash
python scripts/validate.py examples/
```

### 4. Write Your First Capability

```bash
mkdir -p capabilities/your-domain
cp examples/api-testing/rest-client.yaml capabilities/your-domain/my-capability.yaml
# Edit to match your use case
```

## The Problem

Agents claim capabilities without context. "I can debug your API" means nothing without knowing:
- Which environment?
- What log access?
- Current schema version?
- VPN state?
- Required credentials?

**Skills broadcast intentions. But context changes.** VPN disconnects. SSO expires. Dev environments don't log to prod aggregators. The skill doesn't know—it runs anyway and returns confidently wrong results.

## The Solution

**A capability = skill + environment context + truth dependencies**

This framework provides a schema for documenting capabilities as contracts—not marketing copy. Each entry specifies:
- What's required to execute
- What can go wrong
- What honest limitations exist

Before an agent says "I can help", it can check if it *actually* can.

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/preflight.py` | Check if capability requirements are satisfied before execution |
| `scripts/validate.py` | Validate capability YAML files against schema |

## Write a Capability

```yaml
# capabilities/your-domain/my-capability.yaml
id: my-api-client
name: My API Client
domain: development-tooling
version: 1.0.0

action:
  description: Execute CRUD operations against MyService API
  trigger: When testing API endpoints or debugging integration issues

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

## Examples

| File | Description |
|------|-------------|
| [examples/api-testing/rest-client.yaml](examples/api-testing/rest-client.yaml) | Generic REST API testing |
| [examples/observability/log-query.yaml](examples/observability/log-query.yaml) | Log aggregation queries |
| [examples/context-management/session-tracking.yaml](examples/context-management/session-tracking.yaml) | Development session tracking |
| [examples/failure-gallery.md](examples/failure-gallery.md) | **Real failure patterns** — when skills go wrong |

## Schema Reference

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

## Documentation

- [Authoring Guide](docs/authoring.md) — How to write good capability entries
- [Integration Guide](docs/integration.md) — Using capabilities with AI agents
- [Schema Reference](docs/schema-reference.md) — Full schema documentation

## Essays

Why this matters:

- [From Skills to Capabilities](essays/from-skills-to-capabilities.md) — The conceptual argument for why skills aren't enough
- [Context Switching Friction](essays/context-switching-friction.md) — Real-world evidence from work sessions

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

Capabilities can depend on other capabilities:

```yaml
dependencies:
  - database-query        # Need to get IDs first
  - log-aggregator-query  # Then correlate with logs
```

The dependency graph is explicit. If a dependency is blocked, you know before starting.

## Use Cases

1. **Agent Self-Assessment**: Before claiming a capability, verify requirements are met
2. **Onboarding Documentation**: New team members understand what's *actually* available
3. **Incident Response**: Know exactly what tools work in which environments
4. **Capability Planning**: Identify gaps in your tooling coverage
5. **Context Switch Safety**: Re-validate after changing environments, tenants, or credentials

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

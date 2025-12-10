# Schema Reference

Complete reference for the capability schema.

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (lowercase, hyphens only) |
| `name` | string | Yes | Human-readable name |
| `domain` | enum | Yes | Primary domain category |
| `version` | string | Yes | Semantic version (X.Y.Z) |
| `action` | object | Yes | What this capability does |
| `requires` | object | Yes | What's needed to execute |
| `produces` | object | Yes | What this capability outputs |
| `confidence` | object | Yes | Reliability information |
| `metadata` | object | Yes | Authorship and categorization |

## Domain Values

- `context-management` — Workflow and session tracking
- `payment-services` — Payment processing systems
- `development-tooling` — Developer tools and CLIs
- `observability` — Logging, metrics, tracing
- `ci-cd` — Build and deployment pipelines
- `data-engineering` — Data pipelines and processing

## Action Object

```yaml
action:
  description: string  # What it does (required)
  trigger: string      # When it activates (required)
  examples: [string]   # Usage examples (optional)
```

### description

Multi-line description of what this capability does. Be specific about scope and limitations.

### trigger

When/how this capability should be invoked. Include:
- User request patterns
- Automated triggers
- Prerequisite conditions

### examples

Concrete usage examples showing typical invocations.

## Requires Object

```yaml
requires:
  sources_of_truth: [SourceOfTruth]
  access: [string]
  dependencies: [string]
  environment: [string]
  context: [string]
```

### sources_of_truth

```yaml
sources_of_truth:
  - name: string       # Human-readable name (required)
    location: string   # Path, URL, or system (required)
    freshness: enum    # How current it needs to be (required)
    validation: string # How to verify availability (optional)
```

**Freshness values:**
| Value | Meaning | Example |
|-------|---------|---------|
| `real-time` | Must be live | Active DB connection |
| `minutes` | Stale after minutes | API response cache |
| `hours` | Stale after hours | Token validity |
| `daily` | Updated daily | Schema version |
| `weekly` | Updated weekly | Documentation |
| `static` | Doesn't change | CLI binary |

### access

List of access requirements:
- Network access (VPN, firewall rules)
- Credentials (API keys, tokens, passwords)
- Permissions (role-based access)

### dependencies

List of other capability IDs this depends on. The capability won't work unless dependencies are satisfied.

### environment

Runtime requirements:
- Installed tools and versions
- Running services
- Environment variables

### context

Information needed from the user or runtime:
- Target environment
- Resource identifiers
- Configuration choices

## Produces Object

```yaml
produces:
  outputs: [Output]
  side_effects: [string]
```

### outputs

```yaml
outputs:
  - format: string       # Output format (required)
    destination: string  # Where it goes (required)
    consumers: [string]  # What uses it (optional)
```

**Common formats:** JSON, YAML, markdown, text, binary, HTTP response

**Common destinations:** stdout, file, API, database, message queue

### side_effects

State changes this capability causes:
- Database modifications
- File system changes
- External service calls
- Resource consumption

## Confidence Object

```yaml
confidence:
  maturity: enum          # Reliability level (required)
  known_gaps: [string]    # Documented limitations (optional)
  failure_modes: [string] # How it can fail (optional)
  last_validated: date    # When last tested (optional)
```

### maturity

| Level | Criteria |
|-------|----------|
| `experimental` | Proof of concept. May not work. |
| `developing` | Works but has rough edges. |
| `stable` | Reliable for normal use. |
| `battle-tested` | Proven under production pressure. |

### known_gaps

Things that don't work that users might expect to work. Be honest and specific.

### failure_modes

How this capability fails. Include:
- Error messages users will see
- Conditions that trigger failures
- Recovery steps if known

### last_validated

Date when this capability was last tested and confirmed working.

## Metadata Object

```yaml
metadata:
  author: string           # Creator (required)
  created: date           # Creation date (required)
  updated: date           # Last update (optional)
  tags: [string]          # Searchable tags (optional)
  related_skills: [string] # Related resources (optional)
```

## Complete Example

```yaml
id: database-query-runner
name: Database Query Runner
domain: development-tooling
version: 1.0.0

action:
  description: |
    Execute SQL queries against application databases for debugging
    and data inspection. Supports SELECT queries only (read-only mode
    by default).
  trigger: |
    - Investigating data issues
    - Verifying database state after operations
    - Debugging application behavior
  examples:
    - "dbcli query 'SELECT * FROM users WHERE id = 123' --env staging"
    - "dbcli query --file investigate.sql --env production"

requires:
  sources_of_truth:
    - name: Database connection config
      location: ~/.dbcli/connections.yaml
      freshness: static
      validation: "dbcli connections list"
    - name: Current schema
      location: Database information_schema
      freshness: daily
      validation: "dbcli schema show"

  access:
    - Database credentials with SELECT permission
    - Network access to database (VPN for production)
    - Read access to query files

  dependencies: []

  environment:
    - dbcli v3.0+ installed
    - Database client libraries (mysql-client, psql, etc.)

  context:
    - Target environment (dev, staging, production)
    - Target database/schema name

produces:
  outputs:
    - format: Tabular data or JSON
      destination: stdout
      consumers:
        - Manual inspection
        - Script processing with jq
    - format: CSV
      destination: file (with --output flag)
      consumers:
        - Spreadsheet analysis
        - Data export

  side_effects: []  # Read-only queries

confidence:
  maturity: stable
  known_gaps:
    - Write queries blocked by default (use --allow-writes to override)
    - Large result sets (>10k rows) may timeout
    - No support for stored procedure execution
  failure_modes:
    - Wrong credentials return "Access denied" (generic)
    - Network timeout shows "Connection refused"
    - Syntax errors show database-specific messages
  last_validated: 2025-01-15

metadata:
  author: team
  created: 2025-01-01
  updated: 2025-01-15
  tags:
    - database
    - sql
    - debugging
    - data-inspection
  related_skills: []
```

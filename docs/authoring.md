# Authoring Capability Entries

This guide explains how to write capability entries that are honest, useful, and maintainable.

## Core Principles

### 1. Document What's Actually Required, Not What's Ideal

Bad:
```yaml
requires:
  access:
    - API access
```

Good:
```yaml
requires:
  access:
    - VPN connected to internal network
    - Valid merchant ID for target tenant
    - Cybersource sandbox credentials (for token generation)
```

### 2. Known Gaps Are Features, Not Bugs

The `known_gaps` section is where you earn trust. Document:
- What doesn't work that users might expect to work
- Environmental limitations that aren't obvious
- Edge cases that cause silent failures

Example:
```yaml
known_gaps:
  - Dev-CF does NOT log PaymentService to Coralogix (only prod-cf)
  - Log retention limits historical queries (>30 days unavailable)
  - Timezone differences between regions can cause time range mismatches
```

### 3. Failure Modes Tell the Real Story

Think about how this capability fails, not just how it succeeds:

```yaml
failure_modes:
  - VPN disconnect causes connection refused (no helpful error message)
  - Invalid merchant ID returns generic 404 (doesn't say "bad merchant")
  - Wrong applicationName shows empty results (looks like no data exists)
```

### 4. Dependencies Are Contracts

When you list a dependency, you're saying "this capability won't work without that one being available":

```yaml
dependencies:
  - coralogix-payment-log-query  # Can't validate test results without log access
```

### 5. Freshness Matters

Sources of truth have different freshness requirements:

| Freshness | Meaning | Example |
|-----------|---------|---------|
| `real-time` | Must be live/current | Active database connection |
| `minutes` | Stale after minutes | Log query results |
| `hours` | Stale after hours | Cache contents |
| `daily` | Updated daily | Schema versions |
| `weekly` | Updated weekly | Documentation |
| `static` | Doesn't change | CLI binary, config files |

## Template

```yaml
id: kebab-case-id
name: Human Readable Name
domain: context-management | payment-services | observability | development-tooling | ci-cd | data-engineering
version: 1.0.0

action:
  description: |
    Multi-line description of what this capability does.
    Be specific about scope.
  trigger: |
    When/how this capability activates:
    - User request scenario 1
    - Automated trigger scenario
  examples:
    - "Concrete usage example 1"
    - "Concrete usage example 2"

requires:
  sources_of_truth:
    - name: Human readable name
      location: Path, URL, or system identifier
      freshness: real-time | minutes | hours | daily | weekly | static
      validation: "Command or check to verify availability"

  access:
    - Specific access requirement 1
    - Specific access requirement 2

  dependencies:
    - other-capability-id

  environment:
    - Runtime requirement 1
    - Runtime requirement 2

  context:
    - Contextual info needed (ticket IDs, tenant names, etc.)

produces:
  outputs:
    - format: JSON | markdown | text | ...
      destination: stdout | file | API | database | ...
      consumers:
        - What uses this output

  side_effects:
    - State changes this causes

confidence:
  maturity: experimental | developing | stable | battle-tested
  known_gaps:
    - Limitation 1
    - Limitation 2
  failure_modes:
    - How it fails 1
    - How it fails 2
  last_validated: YYYY-MM-DD

metadata:
  author: your-name
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  tags:
    - searchable
    - tags
  related_skills:
    - path/to/related/skill.md
```

## Maturity Levels

| Level | Criteria |
|-------|----------|
| `experimental` | Proof of concept. May not work. Use at own risk. |
| `developing` | Works but has rough edges. Expect issues. |
| `stable` | Reliable for normal use. Known limitations documented. |
| `battle-tested` | Proven under pressure. Used in production incidents. |

## Validation Checklist

Before submitting a capability entry:

- [ ] Can someone unfamiliar with this capability understand what it does?
- [ ] Are all required sources of truth documented with validation steps?
- [ ] Are known gaps honest and specific?
- [ ] Are failure modes based on actual experience, not hypotheticals?
- [ ] Is the maturity level accurate (not aspirational)?
- [ ] Has `last_validated` been updated?

## Anti-patterns

### Don't: Market the capability
```yaml
description: Powerful, enterprise-grade payment testing solution
```

### Do: Describe what it actually does
```yaml
description: Execute payment operations (authorize, capture, refund) against PaymentService API
```

### Don't: Hide limitations
```yaml
known_gaps: []  # "It just works!"
```

### Do: Document real limitations
```yaml
known_gaps:
  - No batch testing mode yet
  - Token generation requires external Cybersource sandbox credentials
```

### Don't: Assume context
```yaml
requires:
  access:
    - Database access
```

### Do: Specify exactly what's needed
```yaml
requires:
  access:
    - MySQL Shell (mysqlsh) installed
    - RDS cluster endpoint for target tenant
    - IAM credentials with rds-db:connect permission
```

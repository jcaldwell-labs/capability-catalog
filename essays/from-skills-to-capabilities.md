# From Skills to Capabilities: The Next Step in Agent Reliability

## The Problem with Skills

Claude Code skills are a breakthrough. They let you encode domain knowledge, workflows, and tool integrations into reusable packages. "Use this skill when debugging payment flows" gives the agent context it wouldn't otherwise have.

But skills have a fundamental gap: **they describe what an agent knows, not what it can actually do right now.**

A skill might say "I can query Coralogix logs to debug payment issues." That's true—in the abstract. But can the agent do it *right now*, in *this environment*, with *current access*?

- Is the VPN connected?
- Does the user have Coralogix credentials?
- Is the target environment even logging to Coralogix? (Spoiler: dev environments often don't.)
- What's the log retention period?

The skill doesn't know. It claims capability without context.

## The Gap Between Claimed and Grounded

This is where agents become unreliable. Not because they're wrong about what they *could* do, but because they're unaware of what they *can* do given current constraints.

An agent confidently runs a Coralogix query against a dev environment that doesn't log there. Returns nothing. "No errors found!" Actually, there were errors—they just weren't in Coralogix.

The agent wasn't lying. It had the skill. It lacked the grounding.

**Claimed capability** = what the agent knows how to do
**Grounded capability** = what the agent can actually execute right now

The gap between these is where trust breaks down.

## Capabilities as Contracts

A capability is a skill plus its full context footprint:

```
capability = skill + environment context + truth dependencies
```

Each capability entry answers:
- **What it does** — the action (same as a skill)
- **What it requires** — sources of truth, access, freshness constraints
- **What it produces** — outputs, formats, downstream consumers
- **Confidence level** — maturity, known gaps, failure modes

The key addition is `requires`. Not aspirational requirements, but hard dependencies:

```yaml
requires:
  sources_of_truth:
    - name: Coralogix access
      location: https://coralogix.com
      freshness: real-time
      validation: "Can authenticate via SSO"

  access:
    - Coralogix account with query permissions
    - Target environment logs to Coralogix (dev-cf does NOT)

  known_gaps:
    - Dev-CF does not log PaymentService to Coralogix
    - Log retention is 30 days
```

Now the agent can do a pre-flight check before claiming capability.

## Pre-flight Validation

Before saying "I can help debug this," the agent checks:

```
✅ Coralogix access: authenticated
✅ Query permissions: confirmed
⚠️ Target environment: dev-cf
   → Known gap: dev-cf does NOT log to Coralogix
   → This capability won't work for this request
```

The agent can now respond honestly:

> "I can't query Coralogix for dev-cf logs because that environment doesn't log there. I can either:
> 1. Query the database directly for transaction state
> 2. Check local PaymentService logs if you have SSH access
> 3. Query prod-cf logs if this issue reproduces in production"

This is more useful than confidently returning empty results.

## Known Gaps as Features

The `known_gaps` field is where capabilities earn trust. It's not a bug list—it's honest documentation of limitations:

```yaml
known_gaps:
  - No automatic retry on transient failures
  - Pagination not supported for large result sets
  - Dev environments don't log to the aggregator
```

These aren't failures to fix. They're constraints to communicate. An agent that surfaces these proactively is more trustworthy than one that discovers them through user frustration.

## Failure Modes Tell the Real Story

Skills describe happy paths. Capabilities document failure modes:

```yaml
failure_modes:
  - VPN disconnect returns "connection refused" (no helpful error)
  - Wrong tenant name shows empty results (looks like no data)
  - Expired token returns generic 401 (doesn't say "token expired")
```

When something goes wrong, the agent can diagnose:

> "Getting 'connection refused'—checking failure modes... this typically means VPN disconnected. Can you verify VPN status?"

Instead of:

> "The query failed. Try again?"

## Composability Through Dependencies

Complex tasks require multiple capabilities. Making dependencies explicit enables validation chains:

```yaml
id: payment-debugging-workflow
requires:
  dependencies:
    - database-query        # Get transaction IDs
    - coralogix-log-query   # Correlate with logs
    - ps-cli-testing        # Reproduce if needed
```

The agent validates the entire chain before starting. If `coralogix-log-query` is blocked (wrong environment), it can suggest alternatives before wasting time on the database query.

## The Evolution

| Stage | What It Provides | Gap |
|-------|------------------|-----|
| **Prompts** | Instructions for a task | No reusability |
| **Skills** | Reusable domain knowledge | No context awareness |
| **Capabilities** | Grounded, validated abilities | — |

Skills are necessary but not sufficient. They encode *what* an agent can do. Capabilities add *whether* it can do it now, *what* might go wrong, and *what* alternatives exist.

## Implications for Agent Development

### 1. Honest Agents Are More Useful

An agent that says "I can't do that here, but I can do this instead" builds more trust than one that tries and fails. Capabilities enable this honesty.

### 2. Validation Before Execution

Instead of discovering blockers mid-task, agents check requirements upfront. This saves time and reduces frustration.

### 3. Better Error Messages

When failures match documented `failure_modes`, agents can provide context-aware diagnostics instead of generic errors.

### 4. Explicit Trade-offs

When multiple approaches exist, agents can explain trade-offs based on `known_gaps`:

> "Option A is faster but doesn't support pagination. Option B handles large results but requires database access. Which constraint matters more?"

### 5. Continuous Improvement

When a capability fails unexpectedly, it's a signal to update `failure_modes`. The catalog becomes living documentation that improves with use.

## What This Isn't

This isn't a replacement for skills. Skills still encode domain knowledge, workflows, and tool integrations. Capabilities wrap skills with runtime context.

This isn't a permission system. Capabilities don't grant or deny access—they document what's required and validate availability.

This isn't foolproof. An agent can still make mistakes. But it can make *fewer* mistakes by checking documented constraints before acting.

## The Path Forward

Skills made agents more knowledgeable. Capabilities make them more honest.

The gap between claimed and grounded capability is where agent reliability breaks down. By documenting requirements explicitly, validating them at runtime, and communicating limitations proactively, we close that gap.

The result: agents that know not just what they *could* do, but what they *can* do—and say so clearly.

---

*This essay accompanies the [Capability Catalog](https://github.com/jcaldwell-labs/capability-catalog), a schema and framework for documenting grounded, composable agent capabilities.*

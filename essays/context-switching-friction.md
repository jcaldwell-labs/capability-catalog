# Context Switching Friction: When Skills Become Distractions

## The Pattern

Reviewing recent work sessions reveals a consistent friction pattern: **skills that work in one context become obstacles in another**.

From the last few days of context logs:

### Friction Type 1: Environment Mismatch

**Database Query Analysis**:
- Triaging a production issue
- Agent has a `database-query` skill
- But: needed access to config management repo, not database
- Skill suggested database queries when the fix was a YAML config change
- Time lost: investigating wrong source of truth

**Feature Testing on Dev Environment**:
- Testing a new feature on dev environment
- Agent has a `log-aggregator-query` skill
- But: dev environments often don't log to the central aggregator
- Session note: "Database column is NULL for all records" — looked like bug
- Reality: nobody had tested with the new flag yet
- Skill led down wrong debugging path because it assumed log availability

### Friction Type 2: Access State Changes

**AWS Infrastructure Investigation**:
- Investigating Lambda function for service health
- Skill knows AWS CLI commands
- But: SSO session had expired
- Commands returned permission errors
- Agent didn't know to check `aws sso login` first

**Binary Build Context**:
- Building a CLI tool from feature branch
- Skill knows `go build` commands
- But: shell cwd kept resetting unexpectedly
- `./scripts/build.sh: Permission denied`
- Capability assumed executable permissions that weren't set

### Friction Type 3: Source of Truth Staleness

**E-commerce Error Triage**:
- Customer can't complete checkout
- Skill knows how to query log aggregator for session IDs
- But: the issue was merchant configuration in a different system
- Account mapping was wrong — not in service logs
- Skill pointed at observable symptoms, not root cause location

**Third-Party Integration Review**:
- PR review for loyalty points redemption
- Skill knows log query patterns
- But: needed to check if OAuth tokens were still valid
- Note: "Token refresh feature not done yet - how handle expired tokens?"
- Capability worked but had dependency on another capability that was blocked

## The Core Problem

Skills encode **what** an agent knows how to do. But execution requires:

1. **Access** — Can I reach the system right now? (VPN, SSO, credentials)
2. **Environment** — Am I in the right context? (dev vs prod, correct tenant)
3. **Source freshness** — Is my information current? (config changes, token expiry)
4. **Dependencies** — Are prerequisite capabilities available?

When any of these change, a skill becomes noise instead of signal.

## Real Examples from Context Logs

### Skill as Distraction

```
Agent: "I'll query the log aggregator for error logs"
Reality: Dev environment doesn't log to the aggregator
Result: Empty results, agent says "no errors found"
Actual: Errors existed, just not in the expected location
```

The skill was accurate. The capability was unavailable. The agent didn't know the difference.

### Skill as Wrong Path

```
Agent: "Let me check the database for record state"
Reality: Records were NULL because feature wasn't tested yet
Result: Agent investigated "bug" that wasn't a bug
Actual: Needed to verify test was actually run first
```

The skill suggested a valid debugging approach. But it wasn't the right *first* step given current context.

### Skill as Time Sink

```
Agent: "Running AWS CLI to check Lambda configuration"
Reality: SSO session expired
Result: Permission denied errors, troubleshooting auth
Actual: Should have checked access first before attempting query
```

The skill worked last session. Access state changed. Agent discovered this mid-task.

## What Capabilities Add

A capability wraps a skill with runtime awareness:

```yaml
id: log-aggregator-query

requires:
  access:
    - Log aggregator SSO authenticated
  environment:
    - Target environment logs to aggregator
  known_gaps:
    - Dev-tenant-A does NOT log to aggregator
    - Dev-tenant-B logs to prod app name, not dev app name
```

Now before invoking the skill, the agent can:

1. **Check access**: Is SSO still valid?
2. **Check environment**: Does this env log to the aggregator?
3. **Surface gaps**: "Note: dev environment logs aren't in the aggregator"

This transforms "confidently wrong" into "honestly limited."

## The Context Switch Problem

Every context switch potentially invalidates capabilities:

| Switch Type | What Breaks |
|-------------|-------------|
| VPN disconnect | Internal service access |
| SSO expiry | AWS, log aggregator, GitHub Enterprise |
| Tenant change | Database connections, log filters |
| Environment change | Dev vs prod access, config differences |
| Time passage | Token expiry, cache staleness |

Skills don't track these. Capabilities can.

## Proposed Solution: Capability Pre-flight

Before executing a skill, check capability requirements:

```
User: "Debug why records aren't saving"

Agent pre-flight check:
├── api-client-testing
│   ├── access: VPN? ✅
│   ├── environment: dev-tenant-B? ✅
│   └── context: tenant ID? ✅
├── database-query
│   ├── access: database connectivity? ✅
│   └── context: correct schema? ✅
├── log-aggregator-query
│   ├── access: SSO valid? ✅
│   ├── environment: dev-tenant-B logs here? ⚠️
│   └── known_gap: "logs to prod app name, not dev app name"
└── Pre-flight result:
    Can proceed, but log queries need app name adjustment
```

The agent now knows:
- Three capabilities are available
- One has an environment nuance to handle
- Can start debugging with correct expectations

## From Distraction to Direction

Without capabilities:
> "I'll check logs... no errors found. Let me try the database... records are NULL. This might be a bug in the save logic..."

With capabilities:
> "Before debugging: this dev environment logs to the prod app name. Let me verify if any test transactions exist first, then check database state, then correlate with logs if needed."

The difference: **knowing what to check first** instead of discovering constraints through failure.

## Implementation Path

1. **Document capabilities** for high-friction skills (done: capability-catalog)
2. **Add runtime checks** — validate access/environment before skill execution
3. **Surface known gaps** proactively — "Note: this environment doesn't log here"
4. **Track access state** — VPN status, SSO expiry, active connections
5. **Pre-flight workflow** — check capabilities before starting complex tasks

The goal isn't to prevent all friction — it's to surface friction *before* it wastes time, transforming skills from potential distractions into grounded capabilities.

---

*This analysis is based on actual work sessions. The friction patterns are real, recurring, and addressable.*

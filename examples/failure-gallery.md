# Failure Gallery: When Skills Go Wrong

Real-world examples of skills causing more harm than help. Not because the skills were wrong, but because context wasn't checked first.

## The Confident Empty Result

**Scenario**: Debug a production error

**What happened**:
```
Agent: "I'll query the log aggregator for errors"
       *runs query*
       "No errors found in the last hour. The service appears healthy."

User:  "But customers are reporting failures right now!"

Agent: "Let me check again... still no errors. Perhaps it's a client-side issue?"
```

**What actually happened**: Dev environment doesn't log to the aggregator. The query succeeded but searched the wrong place.

**With capability pre-flight**:
```yaml
known_gaps:
  - Dev environments do NOT log to aggregator
  - Only prod-tenant-A and prod-tenant-B log here
```

Agent would have said: *"Before I query: which environment is this? Dev environments don't log to the aggregator—I'd need to check local logs instead."*

---

## The Permission Time Sink

**Scenario**: Check AWS Lambda configuration

**What happened**:
```
Agent: "I'll check the Lambda environment variables"
       *runs aws cli command*
       "Error: ExpiredToken - The security token included in the request is expired"

Agent: "Let me try a different approach..."
       *runs another aws command*
       "Error: ExpiredToken..."

Agent: "Interesting, let me check IAM permissions..."
       *15 minutes of troubleshooting*

User:  "Oh, I need to run 'aws sso login' first"
```

**What actually happened**: SSO session had expired. Every AWS command would fail until re-authenticated.

**With capability pre-flight**:
```yaml
requires:
  access:
    - AWS SSO session valid
  # Validation: aws sts get-caller-identity
```

Agent would have checked access first: *"Your AWS session has expired. Run `aws sso login` and I'll continue."*

---

## The Wrong Source of Truth

**Scenario**: Fix a tenant configuration issue

**What happened**:
```
Agent: "I'll check the database for the tenant config"
       *runs database query*
       "Found the tenant. Configuration looks correct."

User:  "But the service is still failing for that tenant"

Agent: "Let me check the service logs..."
       *queries logs*
       "Service shows tenant not found. Database must be out of sync?"

       *30 minutes of investigation*

User:  "Wait, this tenant was added in the config repo, not the database"
```

**What actually happened**: Different configuration sources for different tenants. The skill queried the wrong one.

**With capability pre-flight**:
```yaml
requires:
  context:
    - Tenant configuration source (database vs config repo vs environment variable)
```

Agent would have asked: *"Where is this tenant's config managed? Some use the database, others use the config repo."*

---

## The Stale Context Carryover

**Scenario**: Test API endpoints after switching projects

**What happened**:
```
Agent: "I'll test the /users endpoint"
       *runs API call*
       "Success! Got 200 response with user data."

User:  "That's weird, we don't have a /users endpoint in this project"

Agent: "Let me check... oh, I'm still pointing at the previous project's API"
```

**What actually happened**: Environment variables from previous session carried over. Agent was testing the wrong service.

**With capability pre-flight**:
```yaml
requires:
  environment:
    - API_BASE_URL set to current project
  # Validation: echo $API_BASE_URL
```

Agent would have verified: *"Current API_BASE_URL is `https://other-project.api.com`. Is that correct for this project?"*

---

## The Feature Flag Blindspot

**Scenario**: Debug why a feature isn't working

**What happened**:
```
Agent: "I'll trace through the code path"
       *reads code*
       "The implementation looks correct. Let me check the database state."
       *queries database*
       "Data is correct too. Let me check the logs..."
       *queries logs*
       "No errors. This is puzzling..."

       *1 hour of investigation*

User:  "Is the feature flag enabled in this environment?"

Agent: "...no, it's not."
```

**What actually happened**: Feature was correctly implemented but disabled by feature flag. Code analysis was useless.

**With capability pre-flight**:
```yaml
requires:
  context:
    - Feature flag state for target environment
known_gaps:
  - Cannot check feature flags without config service access
```

Agent would have started with: *"Let me verify the feature flag is enabled in this environment before diving into code."*

---

## The Multi-Tenant Mixup

**Scenario**: Investigate customer-reported issue

**What happened**:
```
Agent: "I'll query for that customer's transactions"
       *runs query*
       "Found 0 transactions for customer ID 12345"

User:  "They definitely made purchases today"

Agent: "Let me check the audit log..."
       *queries*
       "Nothing there either. Perhaps wrong customer ID?"

User:  "Which tenant database did you query?"

Agent: "...the default one. Which tenant is this customer on?"
```

**What actually happened**: Multi-tenant system, agent queried wrong tenant database.

**With capability pre-flight**:
```yaml
requires:
  context:
    - Tenant identifier for target customer
    - Correct database connection string for tenant
```

Agent would have asked: *"Which tenant is this customer on? I need to connect to the right database."*

---

## The Pattern

Every failure above has the same structure:

1. **Skill exists and works** — the agent knows how to do the thing
2. **Context is wrong** — environment, access, or configuration doesn't match
3. **Agent proceeds confidently** — no pre-flight check
4. **Results are misleading** — success (wrong data) or failure (wrong error)
5. **Time is wasted** — investigating symptoms instead of root cause

## The Fix

Capabilities add the pre-flight check:

```
Before executing skill:
├── Check access (credentials, VPN, SSO)
├── Check environment (correct tenant, correct database, correct config)
├── Check context (required identifiers, feature flags, dependencies)
├── Surface known gaps ("dev doesn't log here")
└── Then execute, with appropriate caveats
```

The goal isn't to prevent all mistakes. It's to catch the **predictable** ones—the failures that happen every time context changes, that waste time the same way over and over.

Skills broadcast your intentions. Capabilities check if you can actually execute them.

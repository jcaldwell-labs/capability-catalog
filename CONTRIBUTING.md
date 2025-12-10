# Contributing

Guidelines for contributing to the Capability Catalog.

## Adding a New Capability

1. **Choose the right domain**
   - `context-management` — Workflow and session tracking
   - `development-tooling` — Developer tools, CLIs, SDKs
   - `observability` — Logging, metrics, tracing, monitoring
   - `ci-cd` — Build, test, deployment pipelines
   - `data-engineering` — Data pipelines and processing

2. **Create the capability file**
   ```bash
   mkdir -p capabilities/your-domain
   touch capabilities/your-domain/your-capability.yaml
   ```

3. **Fill in the template**
   See [docs/authoring.md](docs/authoring.md) for the full authoring guide.

4. **Validate against schema**
   ```bash
   # Using yajsv
   yajsv -s schema/capability.schema.yaml capabilities/your-domain/your-capability.yaml
   ```

5. **Test the capability claims**
   - Verify all `sources_of_truth` are accurate
   - Test `validation` commands actually work
   - Confirm `known_gaps` are honest
   - Check `failure_modes` match reality

6. **Submit a PR**
   - One capability per PR (unless related)
   - Include rationale for maturity level
   - Note any testing performed

## Updating Existing Capabilities

When updating a capability:

1. **Increment version** following semver:
   - Patch (1.0.1): Documentation fixes, clarifications
   - Minor (1.1.0): New known gaps, failure modes, expanded examples
   - Major (2.0.0): Breaking schema changes, significant scope changes

2. **Update `metadata.updated`** date

3. **Update `confidence.last_validated`** if you tested

4. **Document what changed** in PR description

## Quality Standards

### Be Honest, Not Optimistic

- `known_gaps` should be comprehensive, not minimal
- `failure_modes` should reflect actual experience
- `maturity` should be accurate, not aspirational

### Be Specific, Not Vague

Bad:
```yaml
access:
  - API access
```

Good:
```yaml
access:
  - API token with read:users scope
  - Network access to api.example.com:443
```

### Be Helpful, Not Bureaucratic

- `validation` commands should actually verify availability
- `examples` should be copy-paste ready
- `failure_modes` should help diagnose, not just list errors

## Schema Changes

Proposing changes to `schema/capability.schema.yaml`:

1. Open an issue first to discuss
2. Ensure backward compatibility when possible
3. Update all example capabilities
4. Update documentation
5. Provide migration guide if breaking

## Code of Conduct

- Be constructive in reviews
- Focus on clarity and usefulness
- Respect that different teams have different needs
- "It works on my machine" is not a validation

## Questions?

Open an issue for:
- Clarification on guidelines
- New domain proposals
- Schema enhancement ideas
- General feedback

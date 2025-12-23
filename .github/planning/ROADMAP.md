# Capability Catalog Roadmap

## Vision

Enable AI agents to honestly assess and communicate their grounded capabilities, reducing the gap between claimed and actual abilities.

## Current State (v1.0)

- Schema definition for capability entries
- Pre-flight validation script
- Schema validation script
- Example capabilities covering common patterns
- Authoring and integration documentation
- Conceptual essays explaining the rationale

## Phase 1: Foundation Hardening

- [ ] Add CI/CD pipeline for automated validation
- [ ] Create GitHub Actions workflow for PR validation
- [ ] Add more example capabilities across domains
- [ ] Improve error messages in validation scripts

## Phase 2: Tooling Enhancement

- [ ] CLI tool for capability management (create, validate, list)
- [ ] Watch mode for development
- [ ] Capability dependency graph visualization
- [ ] Auto-completion support for editors

## Phase 3: Agent Integration

- [ ] Python SDK for runtime capability checking
- [ ] Integration examples for popular AI frameworks
- [ ] Capability registry for shared capabilities
- [ ] Runtime context providers (VPN, credentials, environment)

## Phase 4: Ecosystem

- [ ] Community capability contributions
- [ ] Domain-specific capability packs
- [ ] Integration with skill systems (Claude Code skills, etc.)
- [ ] Metrics and analytics for capability usage

## Design Principles

1. **Honesty over optimism** — Document real limitations
2. **Contracts over descriptions** — Specify requirements explicitly
3. **Composability** — Support capability dependencies
4. **Runtime grounding** — Validate against current context
5. **Developer experience** — Make it easy to write good capabilities

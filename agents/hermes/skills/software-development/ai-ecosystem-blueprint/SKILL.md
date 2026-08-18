---
name: ai-ecosystem-blueprint
description: "Technical blueprint generation for complex AI ecosystems with strict verification standards"
version: 1.0.0
author: Hermes Agent + User
license: MIT
tags: [documentation, audit, verification, architecture, system-blueprint]
related_skills: [hermes-agent, general-planning]
---

# AI Ecosystem Blueprint Generator

> Use `docs/DOCUMENTATION_INDEX.md` to select only the sources for the affected
> area. After the audit, update sources whose criteria changed and update the
> index if documentation was created, moved, replaced, or archived.

This skill provides a methodology for conducting exhaustive technical audits and generating comprehensive system documentation for complex AI agent ecosystems.

## When to Use This Skill

Activate this skill when:
- Generating system architecture documentation
- Conducting technical audits of existing systems
- Creating handoff documentation for development teams
- Performing compliance or security assessments
- Documenting legacy systems with unclear architecture
- Creating technical specifications for system expansion

Key trigger phrases:
- "Document the entire system"
- "Create comprehensive documentation"
- "Audit the system architecture"
- "Generate technical specification"

## Core Principle: Verification Over Assumption

Every technical claim in generated documentation MUST be supported by one or more of these verification methods:

1. **Source Code Inspection**: Direct examination of `.py`, `.ts`, `.js`, `.go`, etc. files
2. **File System Analysis**: Verified via `ls -la`, `find`, `read_file` tools
3. **Process Verification**: Confirmed running processes via `ps aux`, service status
4. **Configuration Audit**: Examined config files via `read_file`
5. **Command Execution**: Actual command outputs, not assumed behavior
6. **System Properties**: Verified package versions via `pip list` or equivalent

## Methodology

### Phase 1: Discovery
1. **Project structure mapping**:
   ```bash
   find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' | head -500
   ```
2. **Key file identification**: Locate manifests, entry points, configs
3. **Service discovery**: List running processes, systemd services, cron jobs
4. **Memory/config location mapping**: Identify Hermes, Claude, and system-level configs

### Phase 2: Static Analysis
1. For each module/source file:
   - Identify purpose and entrypoints
   - Map imports (internal and external)
   - Identify file read/write operations
   - Map service interactions
2. **Cross-reference** documentation claims with actual implementation
3. Document actual dependency versions (not just declared)

### Phase 3: Configuration Analysis
1. Locate ALL configuration sources:
   - Global configs (`~/.hermes/config.yaml`)
   - Project-local configs (`.env`, `.claude.json`)
   - Service configs (`/etc/systemd/`, etc.)
2. Map configuration precedence (which overrides which)
3. Document actual values, not expected values

### Phase 4: Verification
1. **Critical commands**: Verify all documented commands actually execute correctly
2. **Service status**: Confirm services are actually running or stopped as documented
3. **Dependency reality check**: Compare declared vs. actual installed packages
4. **Secrets verification**: Confirm existence of secrets without exposing values

### Phase 5: Documentation Generation
Structure the output following the SYSTEM_BLUEPRINT.md format:
1. Executive Summary
2. Verified System Overview
3. Architecture Components
4. Component Catalog
5. Dependency Analysis
6. Verification Results
7. Configuration Details
8. Operational Procedures
9. Troubleshooting Guide

## Critical Rules

### DO NOT:
- Assume a component exists because it's named in documentation
- Infer functionality from file names or directory structures
- Copy-paste dependency lists without verifying actual installation
- Include speculative architectures or hypothetical flows
- Document secrets or credentials (even redacted ones in plain text)
- Trust documentation over source code

### DO:
- Trace every claim to concrete evidence (file, command output, configuration)
- Verify command syntax with `--help` before documenting
- Confirm service definitions against actual systemd/service files
- Cross-reference documentation against actual code behavior
- Document discrepancies between documentation and reality explicitly
- Mark uncertain information as "DETERMINED" with explanation of uncertainty

## Output Format

Generated documentation must include:
1. **Evidence Chain**: For each component, list verification sources
2. **Verification Status**: VERIFIED, INFERRED, or NO DETERMINADO for each claim
3. **Exact Paths**: All file paths explicitly stated, not relative references
4. **Command Examples**: Only commands that have been verified to work
5. **Version Pinning**: Actual versions, not minimum requirements

## Pitfalls & Anti-Patterns

1. **Documentation Drift**: Project documentation often lags behind implementation. Always verify against code first.
2. **Implicit Dependencies**: Components may rely on services not explicitly declared. Use `strace`, `lsof`, or code inspection to find hidden relationships.
3. **Environment-Specific Behavior**: Configurations may differ significantly between environments. Document the specific environment audited.
4. **Stale References**: Old scripts, configs, and backups may appear active but are unused. Cross-check with actual execution paths.
5. **Permission Issues**: Verify not just file existence but also accessibility with current user context.

## Related Documentation

- `references/verified_components_list.md` - Inventory of all components found during latest audit
- `references/system_state_verification.md` - Commands and outputs used to verify system state

## Example Usage

```bash
# Begin technical audit
hermes --skill ai-ecosystem-blueprint
# Then execute phases 1-5 above for the target system
```

The output should be a SYSTEM_BLUEPRINT.md file that any new team member can use to understand the system without independent investigation.

# Documentation Management System

## 📋 Overview

This document contains guidelines for documentation updates, including prompts modifications, README changes, and automation setup for ensuring consistent and automated documentation updates when making significant changes.

## 📋 System Prompt Modifications

### Automated Documentation Updates

**When to update documentation:**
- When adding new skills or components
- When making significant changes to existing components
- When changes affect the architecture or workflow
- When fixing bugs in core components

**Automated triggers:**
```bash
# Hook system to automatically update documentation
npx @hermes/cli@latest hooks trigger --type documentation-update
```

**Manual triggers for documentation updates:**
1. Run `./generate-specs.sh` to generate OpenSpec specifications
2. Update README.md with new section for documentation practices
3. Update CLAUDE.md with system prompt modifications
4. Verify all documentation is current and complete

## 📋 Key Documentation Files

| File | Purpose | Update Frequency | Check Method |
|------|---------|------------------|--------------|
| README.md | Project overview and documentation | After significant changes | Manual review |
| CLAUDE.md | System prompts and rules | After prompt modifications | Automated validation |
| .openspec/specs/ | OpenSpec specifications | After code changes | Automated validation |
| skills/*/SKILL.md | Individual skill documentation | After skill changes | Automated validation |
| CHANGELOG.md | Change history | With each release | Automated with hooks |

## 📋 Automation Setup

### Automated validation
```bash
# Validate all documentation
./validate-documentation.sh

# Auto-generate OpenSpec specs
./generate-specs.sh

# List all specs
./list-all-specs.sh
```

### Automated hooks
```bash
# Trigger documentation updates after task completion
npx @hermes/cli@latest hooks post-task --task-id "[task-id]" --type documentation-update

# Run health checks
orchestrator-main "health-check" --documentation
```

### Validation commands
- `./test-documentation.sh` - Validate README updates
- `./validate-skills.sh` - Validate skill documentation
- `./validate-specs.sh` - Validate OpenSpec specifications

## 📋 Best Practices

### Documentation update workflow
1. **Identify**: Recognize when documentation needs updates
2. **Update**: Modify relevant documentation files
3. **Verify**: Run validation scripts
4. **Commit**: Use clear commit messages

### Documentation commit messages
- `docs: update README - added automated documentation section`
- `docs: update CLAUDE.md - added system prompt modifications`
- `docs: update README - added new documentation section`
- `docs: update orchestrator-main - added health check documentation`

### Validation
Always run:
```bash
pnpm run test
./generate-specs.sh
./list-all-specs.sh
```

## 📋 Testing Documentation

### Test documentation updates
```bash
# Test README updates
test-readme-updates.sh

# Test documentation structure
./test-docs-structure.sh

# Validate OpenSpec
./validate-specs.sh
```

### Verification commands
- `./verify-documentation.sh` - Complete documentation validation
- `./update-documentation.sh` - Automated documentation update
- `./check-documentation.sh` - Check if documentation is up-to-date

## 📋 Previous Changes

### Pending changes:
1. ✅ Updated README.md with documentation management section
2. ✅ Updated CLAUDE.md with system prompt modifications
3. ✅ Created scripts for documentation automation
4. ✅ Added validation and testing scripts

### Changes applied:
1. ✅ Updated README.md with comprehensive documentation practices
2. ✅ Updated CLAUDE.md with system prompt modifications
3. ✅ Added documentation update workflow and automation setup

## 📋 Future enhancements

1. **Add JSDoc comments** to skill documentation
2. **Implement documentation linting** scripts
3. **Create automated documentation preview** system
4. **Add documentation templates** for quick updates
5. **Implement documentation versioning** system

## 📋 Usage examples

```bash
# Update documentation after making changes
./update-documentation.sh

# Validate documentation
./validate-documentation.sh

# Test documentation
./test-documentation.sh

# Quick documentation check
./quick-docs-check.sh
```

## 📋 Conclusion

The documentation management system ensures consistent updates, validation, and maintenance of all project documentation. By automating documentation updates and providing clear workflows, we maintain high-quality documentation that reflects the current state of the project.

## 📋 Key files for documentation management

| File | Purpose |
|------|---------|
| README.md | Project overview and documentation management | 
| CLAUDE.md | System prompts and rules for documentation management | 
| scripts/ | Documentation automation scripts | 
| .openspec/specs/ | OpenSpec specifications for documentation | 
| skills/ | Individual skill documentation | 
| CHANGELOG.md | Documentation change history |

## 📋 Next steps

1. Add JSDOc comments to skills
2. Implement documentation linting
3. Create documentation templates
4. Add documentation versioning
5. Implement automated documentation preview

## 📋 Contact

For documentation issues or questions, contact the documentation team.

## 📋 Documentation update process

### Update process
1. Identify when documentation needs to be updated
2. Update the relevant documentation files
3. Run validation scripts
4. Commit changes with clear messages

### Validation process
1. Run validation scripts
2. Check that all specifications are current
3. Verify that README is accurate and complete
4. Ensure that all skills are documented correctly

## 📋 Summary

The documentation management system ensures that documentation is kept up-to-date and accurate. By automating documentation updates and providing clear workflows, we maintain high-quality documentation that reflects the current state of the project.

## 📋 Key Takeaways

1. Always update documentation when making significant changes
2. Use automated validation scripts to verify documentation
3. Maintain a clear documentation update workflow
4. Keep documentation up-to-date and accurate

## 📋 Best practices for documentation

1. Update documentation before running tests
2. Use clear and consistent commit messages
3. Follow the documentation update workflow
4. Validate documentation after updates
5. Keep documentation up-to-date and accurate

## 📋 Common issues and solutions

### Issue: Documentation not up-to-date
**Solution**: Run the documentation update scripts regularly and ensure that the documentation is validated before committing.

### Issue: Tests failing due to documentation
**Solution**: Update the documentation to reflect the current state of the project and run the validation scripts to ensure that the documentation is correct.

### Issue: Validation scripts failing
**Solution**: Check the validation scripts for errors and fix them. Then, run the validation scripts again to ensure that they pass.

### Issue: Documentation not being updated
**Solution**: Ensure that the documentation update hooks are configured correctly and that they are being triggered automatically when changes are made.

## 📋 Next steps

1. Add JSDOc comments to skills
2. Implement documentation linting scripts
3. Create documentation templates
4. Add documentation versioning
5. Implement automated documentation preview

## 📋 Testing the documentation

### Testing documentation updates
```bash
# Test README updates
test-readme-updates.sh

# Test documentation structure
./test-docs-structure.sh

# Validate OpenSpec
./validate-specs.sh
```

### Verify documentation
```bash
# Verify documentation
./verify-documentation.sh

# Update documentation
./update-documentation.sh

# Check documentation
./check-documentation.sh

# Quick documentation check
./quick-docs-check.sh
```

## 📋 Documentation examples

```bash
# Example: Update orchestrator-main documentation
# 1. Identify changes made to orchestrator-main
# 2. Update documentation
# 3. Run validation scripts
# 4. Commit changes

# Example: Documentation update workflow
# 1. Identify when documentation needs to be updated
# 2. Update the relevant documentation files
# 3. Run validation scripts
# 4. Commit changes with clear messages
```

## 📋 Documentation management tips

1. **Consistent format**: Use consistent markdown formatting across all documentation files
2. **Update frequently**: Update documentation frequently, especially after making significant changes
3. **Automate when possible**: Use automation scripts to update documentation when possible
4. **Validate consistently**: Run validation scripts regularly to ensure documentation is accurate
5. **Keep documentation up-to-date**: Update documentation regularly to reflect the current state of the project

## 📋 Documentation best practices

1. **Update documentation before running tests**: This ensures that the tests are testing the correct functionality
2. **Use clear commit messages**: This helps other team members understand what changes were made
3. **Follow the documentation update workflow**: This ensures that all changes are documented consistently
4. **Validate documentation after updates**: This ensures that the documentation is accurate
5. **Keep documentation up-to-date**: This ensures that the documentation reflects the current state of the project
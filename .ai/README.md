# AI-Assisted Development Documentation

This directory contains the AI-assisted development framework for PETsARD, including development workflow automation and Roo integration.

## 🎯 Overview

The `.ai/` directory provides:
- **Development Workflow Automation**: Tools to ensure consistent development practices
- **Roo Integration**: AI assistant configuration for project-specific context
- **Architecture Enforcement**: Automated checks for design principle compliance

## 📁 Directory Structure

```
.ai/
├── README.md                    # This overview document
├── SETUP-GUIDE.md              # Quick setup guide for developers
├── development-workflow.md      # Detailed development process documentation
└── roo-config/                  # Roo AI assistant configuration
    ├── project-context.md       # Project context and architecture principles
    └── architecture-rules.md    # Architecture rules and development reminders
```

## 🚀 Quick Start

### For New Developers

1. **Setup Development Environment**:
   ```bash
   # Follow the setup guide
   cat .ai/SETUP-GUIDE.md
   ```

2. **Configure Roo**:
   - Roo will automatically load `.roo/project.yaml`
   - Context files in `.ai/roo-config/` will be auto-loaded

3. **Start Development**:
   - Use Roo for AI-assisted development
   - Follow the architecture principles in `.ai/roo-config/`

### For Existing Developers

The development workflow now includes:
- **Architecture Compliance**: Automated checks for design principle adherence
- **AI-Assisted Development**: Roo integration with project-specific context

## 🔧 Key Features

### 1. Roo AI Assistant Integration
- **Project Context Loading**: Automatically loads architecture principles and coding standards
- **Architecture Rule Enforcement**: Reminds developers of module-specific design constraints

### 2. Architecture Guidelines
- **Clear Principles**: Maintaining system consistency
- **Development Best Practices**: Standardized approaches for common development tasks

## 📋 Development Workflow

### Daily Development Process

1. **Before Coding**:
   - Review architecture principles in `.ai/roo-config/`
   - Use Roo for context-aware assistance

2. **During Development**:
   - Roo provides context-aware assistance
   - Architecture rules are automatically enforced
   - API consistency is maintained

3. **Before Committing**:
   ```bash
   git add .
   git commit -m "feat(evaluator): 新增隱私評估器"
   ```

### Architecture Principles Enforced

- **Module Separation**: Clear boundaries between modules
- **Functional Programming**: Pure functions and immutable data structures
- **Type Safety**: Complete type annotations for all public APIs
- **Backward Compatibility**: API stability maintenance
- **Unified Interfaces**: Consistent patterns across modules

## 🎯 Benefits

### For Individual Developers
- **Faster Onboarding**: Complete context available through AI assistant
- **Consistent Development**: Architecture principles enforcement
- **Reduced Errors**: Architecture compliance checks prevent common mistakes

### For Team Collaboration
- **Unified Architecture**: All developers follow the same design principles
- **Knowledge Sharing**: Architecture principles documented in `.ai/roo-config/`

### For Project Maintenance
- **Architecture Integrity**: Systematic enforcement of design decisions
- **Quality Assurance**: Automated checks for common architectural violations

## 🔗 Related Resources

- **[Setup Guide](SETUP-GUIDE.md)**: Quick start for new developers
- **[Development Workflow](development-workflow.md)**: Detailed process documentation
- **[Project Context](roo-config/project-context.md)**: Architecture principles and standards
- **[Architecture Rules](roo-config/architecture-rules.md)**: Specific compliance requirements

## 📞 Support

For questions about the AI-assisted development framework:
1. Check the [Setup Guide](SETUP-GUIDE.md) for common issues
2. Review the [Development Workflow](development-workflow.md) for detailed processes
3. Consult the architecture documentation in `roo-config/` for guidance

---

🎉 **Welcome to AI-Assisted PETsARD Development!**

This framework ensures consistent, high-quality development while maintaining architectural integrity across the entire team.
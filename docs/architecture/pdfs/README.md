# TOSCA Architecture Documentation - PDF Collection

**Generated:** 2025-11-05
**Version:** v0.9.13-alpha
**Format:** PDF with embedded PNG diagrams

This directory contains professionally formatted PDF versions of all TOSCA architecture documentation with embedded high-resolution PlantUML diagrams.

---

## Features

✓ **Professional Layout** - 0.35in margins for maximum content density
✓ **Embedded Diagrams** - High-quality PNG architecture diagrams
✓ **Navigation** - Table of contents with blue hyperlinks
✓ **Hyperlinks** - All internal and external links in blue
✓ **Consistent Styling** - Professional typography and formatting

---

## Core Architecture Documents

### System Overview & Design

| Document | Description | Size |
|----------|-------------|------|
| [01_system_overview.pdf](01_system_overview.pdf) | High-level system architecture, technology stack, hardware components | 459 KB |
| [02_database_schema.pdf](02_database_schema.pdf) | Complete SQLite schema with ERD diagram | 693 KB |
| [03_safety_system.pdf](03_safety_system.pdf) | Safety architecture, interlocks, state machine | 366 KB |
| [04_treatment_protocols.pdf](04_treatment_protocols.pdf) | Protocol engine, execution model, data flow | 702 KB |
| [05_image_processing.pdf](05_image_processing.pdf) | Computer vision pipeline, ring detection, focus measurement | 115 KB |

### Implementation Details

| Document | Description | Size |
|----------|-------------|------|
| [06_protocol_builder.pdf](06_protocol_builder.pdf) | Protocol builder UI and action-based model | 418 KB |
| [07_safety_watchdog.pdf](07_safety_watchdog.pdf) | Hardware watchdog implementation (Arduino) | 110 KB |
| [08_security_architecture.pdf](08_security_architecture.pdf) | Security design, encryption plan (Phase 6) | 117 KB |
| [09_test_architecture.pdf](09_test_architecture.pdf) | Testing strategy, mock infrastructure, test patterns | 665 KB |
| [10_concurrency_model.pdf](10_concurrency_model.pdf) | Threading, asyncio/PyQt6 integration, thread safety | 659 KB |
| [11_asyncio_pyqt6_integration.pdf](11_asyncio_pyqt6_integration.pdf) | Async patterns with Qt event loop | 112 KB |
| [11_event_logging.pdf](11_event_logging.pdf) | Event logging architecture and immutability | 110 KB |
| [12_recording_manager.pdf](12_recording_manager.pdf) | Video recording and session data management | 116 KB |
| [13_calibration_procedures.pdf](13_calibration_procedures.pdf) | Hardware calibration workflows | 109 KB |

---

## Architecture Decision Records (ADRs)

| Document | Description | Size |
|----------|-------------|------|
| [ADR-001-protocol-consolidation.pdf](ADR-001-protocol-consolidation.pdf) | Protocol model unification decision | 96 KB |
| [ADR-002-dependency-injection-pattern.pdf](ADR-002-dependency-injection-pattern.pdf) | Hardware controller DI pattern | 97 KB |
| [ADR-003-pyqt6-gui-framework.pdf](ADR-003-pyqt6-gui-framework.pdf) | PyQt6 framework selection rationale | 98 KB |
| [ADR-004-sqlite-database.pdf](ADR-004-sqlite-database.pdf) | SQLite database choice and encryption plan | 95 KB |
| [ADR-005-arduino-gpio-migration.pdf](ADR-005-arduino-gpio-migration.pdf) | Arduino migration from FT232H | 97 KB |
| [ADR-006-selective-shutdown-policy.pdf](ADR-006-selective-shutdown-policy.pdf) | Safety shutdown policy rationale | 97 KB |
| [ADR-TEMPLATE.pdf](ADR-TEMPLATE.pdf) | Template for future ADRs | 89 KB |

---

## Additional Documentation

| Document | Description | Size |
|----------|-------------|------|
| [00_IMPLEMENTATION_STATUS.pdf](00_IMPLEMENTATION_STATUS.pdf) | Current implementation status across all modules | 100 KB |
| [SAFETY_SHUTDOWN_POLICY.pdf](SAFETY_SHUTDOWN_POLICY.pdf) | Detailed safety shutdown rationale | 97 KB |
| [QUALITY_ATTRIBUTES.pdf](QUALITY_ATTRIBUTES.pdf) | Quality attribute requirements and scenarios | 102 KB |
| [SECURITY_THREAT_MODEL.pdf](SECURITY_THREAT_MODEL.pdf) | Security threat analysis and mitigations | 104 KB |
| [hardware_controller_base_usage.pdf](hardware_controller_base_usage.pdf) | HAL base class usage guide | 109 KB |

---

## Embedded Diagrams

All PDFs include relevant PlantUML C4 model diagrams:

1. **TOSCA System Context** - External system boundaries and actors
2. **TOSCA Container Diagram** - High-level 3-layer architecture
3. **TOSCA Component Diagram - Application Core** - Core business logic components
4. **TOSCA Component Diagram - HAL** - Hardware abstraction layer
5. **TOSCA Database Schema ERD** - Complete entity-relationship diagram
6. **TOSCA Data Architecture** - Data flow and storage patterns
7. **TOSCA Data Flow Diagram** - Real-time data processing pipeline
8. **TOSCA Treatment Workflow Sequence** - Treatment execution sequence

---

## Regenerating PDFs

To regenerate PDFs from source markdown files:

```bash
cd /mnt/c/Users/wille/Desktop/TOSCA-dev/docs/architecture

# Single file
python3 generate_pdfs.py --file 01_system_overview.md

# All files
python3 generate_pdfs.py --all
```

### Configuration

Edit `pdf-generation-config.json` to:
- Map diagrams to specific documents
- Adjust pandoc options
- Change PDF engine (wkhtmltopdf recommended)

Edit `pdf-styles.css` to customize:
- Page margins (currently 0.35in)
- Typography and colors
- Table and code block styling
- Hyperlink colors (currently blue: #2e86de)

---

## Medical Device Compliance

**IMPORTANT:** These documents describe a medical device laser control system currently in **RESEARCH MODE**.

- ⚠️ **NOT FDA-cleared** for clinical use
- ⚠️ **Encryption NOT implemented** (Phase 6 planned)
- ⚠️ **NOT for protected health information (PHI)**

Current phase: **Phase 5 - Testing & Quality Assurance**

---

## Version History

- **v0.9.13-alpha (2025-11-05):** PDF generation with embedded diagrams, blue hyperlinks, compact layout
- **v0.9.12-alpha (2025-11-02):** Comprehensive hardware mock infrastructure, documentation unification
- **v0.9.11-alpha (2025-10-30):** Architecture analysis complete (Grade: A - Excellent)

---

## Contact

**Project:** TOSCA Laser Control System
**Repository:** https://github.com/will-aleyegn/TOSCA_DEV
**Documentation:** `docs/architecture/`

For questions or updates, refer to `CLAUDE.md` in the project root.

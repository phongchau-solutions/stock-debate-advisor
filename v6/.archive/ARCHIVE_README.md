# 📦 Documentation Archive

**Last Updated:** January 14, 2026  
**Archival Reason:** Documentation cleanup - consolidation of redundant and obsolete files

---

## 📋 Archived Files

### Legacy Pipeline Documentation
**Status:** Archived - Superseded by canonical documentation

| File | Reason | Replacement |
|------|--------|-------------|
| `PIPELINE_FIXED_SUMMARY.md` | Dated status report (Jan 10) | [DATA_PIPELINE_V2.md](../DATA_PIPELINE_V2.md) |
| `PIPELINE_REBUILD_SUMMARY.md` | Dated status report (Jan 10) | [DATA_PIPELINE_V2.md](../DATA_PIPELINE_V2.md) |
| `FILE_MANIFEST.md` | Outdated file listing | [README.md](../README.md) |
| `CLEANUP_SUMMARY.md` | VietCap API cleanup summary | [DATA_PIPELINE_V2.md](../DATA_PIPELINE_V2.md) |
| `YAHOO_FINANCE_SERVICE_SUMMARY.md` | Service-specific summary | [data-service/README.md](../data-service/README.md) |

**Why Archived:**
- Multiple files documented the same data pipeline rebuild (Jan 10, 2026)
- Consolidation into canonical `DATA_PIPELINE_V2.md` as single source of truth
- Status files become outdated quickly; replaced with live documentation
- Service-specific docs should live in service directories, not root

---

### Deprecated Framework Documentation
**Status:** Archived - Framework replaced in v6

| File | Reason | Note |
|------|--------|------|
| `CREWAI_INDEX.md` | CrewAI framework deprecated | v6 migrated to Google ADK |

**Why Archived:**
- v6 project completed migration from CrewAI to Google Agent Development Kit (ADK)
- CrewAI documentation no longer relevant to current architecture
- Google ADK documentation in [ADK_INTEGRATION.md](../ADK_INTEGRATION.md)

---

## 🔍 What to Use Instead

### For Data Pipeline Information
→ **[DATA_PIPELINE_V2.md](../DATA_PIPELINE_V2.md)** (Canonical)
- Complete schema documentation
- Service architecture
- FastAPI endpoints
- Airflow DAG details

### For Service-Specific Details
→ **Service READMEs:**
- [data-service/README.md](../data-service/README.md)
- [analysis-service/README.md](../analysis-service/README.md)
- [agentic-service/README.md](../agentic-service/README.md)
- [frontend/README.md](../frontend/README.md)

### For Project Overview
→ **[README.md](../README.md)** (Primary reference)
→ **[PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md)** (Current status)

### For PM/Management Docs
→ **[PM_COMMAND_CENTER.md](../PM_COMMAND_CENTER.md)** (Strategic hub)
→ **[EXECUTIVE_SUMMARY.md](../EXECUTIVE_SUMMARY.md)** (Status report)
→ **[PM_DASHBOARD.md](../PM_DASHBOARD.md)** (Metrics & progress)

### For Google ADK Details
→ **[ADK_INTEGRATION.md](../ADK_INTEGRATION.md)** (Framework integration)

---

## 📦 Archive Location

```
v6/.archive/
├── PIPELINE_FIXED_SUMMARY.md
├── PIPELINE_REBUILD_SUMMARY.md
├── FILE_MANIFEST.md
├── CLEANUP_SUMMARY.md
├── YAHOO_FINANCE_SERVICE_SUMMARY.md
├── CREWAI_INDEX.md
└── ARCHIVE_README.md (this file)
```

**Retention Policy:**
- Kept for historical reference only
- Do not use for new development
- May be deleted after v1.0 release (March 31, 2026)
- Contact PM for historical context if needed

---

## ✅ Documentation Cleanup Summary

**Date:** January 14, 2026  
**Changes Made:**
- ✅ Archived 5 redundant pipeline status documents
- ✅ Archived 1 deprecated framework documentation file
- ✅ Consolidated information into canonical source documents
- ✅ Updated cross-references in main README.md
- ✅ Created this archive index for historical tracking

**Documentation is now:**
- ✅ Less redundant (single source of truth)
- ✅ More maintainable (fewer files to update)
- ✅ Better organized (service docs in service directories)
- ✅ More current (no stale status reports in main directory)

---

## 📞 Questions?

For context on archived documents:
- **PM Questions:** Contact PM via [PM_COMMAND_CENTER.md](../PM_COMMAND_CENTER.md)
- **Technical Questions:** Check main [README.md](../README.md) or relevant service README
- **Historical Context:** Check this file or the archived documents themselves

---

**Archive Created By:** PM (Documentation Cleanup Sprint)  
**Related:** Documentation cleanup task, January 14, 2026

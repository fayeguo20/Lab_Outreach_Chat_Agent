# 07 - Content Management

> **Priority:** 🟢 Low  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 📚 Current Knowledge Base

### Indexed Documents

| File | Type | Size | Description |
|------|------|------|-------------|
| lab_overview.txt | TXT | ~5KB | Structured summary for broad questions |
| Human Tumor Atlas Network paper.pdf | PDF | ~15MB | HTAN research |
| CODEX_paper_Cell_2018.pdf | PDF | ~20MB | CODEX technology |
| IBEX_Nat_Protocols_2022.pdf | PDF | ~10MB | IBEX methodology |
| PanIN_paper.pdf | PDF | ~15MB | Pancreatic research |
| Spatial_biology_paper_2024.pdf | PDF | ~25MB | Recent spatial biology |
| README.txt | TXT | ~1KB | Index description |

**Total:** ~92MB across 7 files

### Storage Location
- **Local:** `outreach/assets/knowledge_base/`
- **Cloud:** Google File Search Store `hickey-lab-knowledge-base`

---

## 📥 Adding New Documents

### Process

```bash
# 1. Add file to local knowledge base
cp new_paper.pdf outreach/assets/knowledge_base/

# 2. Sync to Google File Search
cd outreach
python tools/manage_store.py sync

# 3. Verify upload
python tools/manage_store.py list
```

### File Requirements

| Requirement | Value |
|-------------|-------|
| Max file size | 100MB (Gemini limit) |
| Supported formats | PDF, TXT, MD, HTML, CSV |
| Naming convention | `descriptive_name.pdf` |
| No spaces in names | Recommended |

### Quality Checklist

Before adding a document:
- [ ] Is it relevant to lab outreach?
- [ ] Is it publicly shareable?
- [ ] Is the PDF text-extractable (not scanned images)?
- [ ] Is it the final/published version?
- [ ] Does it have proper metadata?

---

## 🗑️ Removing Documents

### Process

```bash
# 1. Remove from local
rm outreach/assets/knowledge_base/old_paper.pdf

# 2. Remove from Google File Search
python tools/manage_store.py list  # Get file ID
python tools/manage_store.py delete <file_id>
```

### When to Remove
- Paper retracted or corrected
- Outdated information
- Replaced by newer version
- Copyright issues

---

## 📝 Content Guidelines

### What to Include

✅ **Good candidates:**
- Published peer-reviewed papers
- Lab overview/mission documents
- Methodology descriptions
- Public presentations
- FAQ documents
- Team bios (if public)

### What NOT to Include

❌ **Avoid:**
- Unpublished research
- Confidential data
- Patient information
- Grant applications
- Internal communications
- Proprietary methods

---

## 🔄 Content Update Workflow

### Regular Updates (Monthly)

```markdown
1. Review: Are there new publications?
2. Gather: Collect PDFs from lab members
3. Review: Check quality guidelines
4. Upload: Add to knowledge base
5. Test: Ask questions about new content
6. Document: Update this log
```

### Content Review Log

| Date | Action | Document | Notes |
|------|--------|----------|-------|
| 2024-12-16 | Added | lab_overview.txt | Created for broad questions |
| 2024-12-16 | Initial | 5 PDFs | Initial knowledge base |
| | | | |

---

## 📊 Content Quality Monitoring

### Metrics to Track

| Metric | How to Measure |
|--------|----------------|
| Coverage gaps | Questions with "I don't know" responses |
| Outdated info | User feedback, periodic review |
| Accuracy | Spot-check responses against sources |
| Relevance | Track which documents get cited |

### Identifying Gaps

Monitor for patterns like:
- "I don't have information about X"
- Repeated questions about missing topics
- User feedback about incomplete answers

### Filling Gaps

1. Document missing topics
2. Prioritize by frequency
3. Create content or find existing docs
4. Add to knowledge base
5. Test and verify

---

## 🤖 The `lab_overview.txt` File

### Purpose
This file provides structured context for broad questions that might not be directly answered by individual papers.

### Structure

```markdown
# Hickey Lab Overview

## Mission
[Brief mission statement]

## Research Areas
- Area 1: Description
- Area 2: Description

## Key Technologies
- CODEX: What it is, what it does
- IBEX: What it is, what it does

## Team
- PI: Dr. John Hickey
- Key members (if public)

## Publications
- Summary of major papers
- Links to full papers

## Contact
- Website
- Email (if public)
```

### When to Update
- New research areas
- Team changes
- Major publications
- Mission updates

---

## 🔐 Content Access Control

### Current Model
- All indexed content is queryable by anyone
- No user-based restrictions
- Public knowledge only

### Future Considerations
- Tiered access (public vs. authenticated)?
- Content for specific audiences (students vs. researchers)?
- Restricted research previews?

---

## 📋 Content Management Checklist

### Adding Content
- [ ] Document is publicly shareable
- [ ] PDF is text-extractable
- [ ] Filename is descriptive
- [ ] Uploaded to File Search store
- [ ] Tested with relevant questions
- [ ] Logged in content review log

### Removing Content
- [ ] Documented reason for removal
- [ ] Removed from local folder
- [ ] Removed from File Search store
- [ ] Verified removal
- [ ] Logged in content review log

### Periodic Review (Monthly)
- [ ] Check for new publications
- [ ] Review user feedback for gaps
- [ ] Test existing content accuracy
- [ ] Update lab_overview.txt if needed
- [ ] Update documentation

---

## ❓ Open Questions

1. Who is responsible for adding new content?
2. How often should we update?
3. Should we include preprints?
4. What's the process for content approval?
5. How do we handle sensitive research?

---

## 📎 References

- [Gemini File Upload Limits](https://ai.google.dev/gemini-api/docs/document-processing)
- [Store Manager Tool](../outreach/tools/manage_store.py)
- [Knowledge Base Folder](../outreach/assets/knowledge_base/)

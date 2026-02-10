# WW3 Reference Output Availability Tracker

This file tracks which regression tests have reference outputs available for comparison.

**Status Legend:**
- ⏳ **Pending**: Reference outputs not yet generated
- ✅ **Available**: Reference outputs present and validated
- ⚠️ **Partial**: Some output files missing
- ❌ **Failed**: Generation failed or outputs invalid

**Last Updated**: 2026-02-10

---

## Phase 1: tp1.x Tests (1-D Propagation)

| Test | Status | Files | Size | Checksum | Notes |
|------|--------|-------|------|----------|-------|
| tp1.1 | ⏳ | 0 | 0 MB | ❌ | Equatorial propagation |
| tp1.2 | ⏳ | 0 | 0 MB | ❌ | Meridional propagation |
| tp1.3 | ⏳ | 0 | 0 MB | ❌ | Monochromatic shoaling |
| tp1.4 | ⏳ | 0 | 0 MB | ❌ | Spectral refraction (X) |
| tp1.5 | ⏳ | 0 | 0 MB | ❌ | Spectral refraction (Y) |
| tp1.6 | ⏳ | 0 | 0 MB | ❌ | Wave-current interaction |
| tp1.7 | ⏳ | 0 | 0 MB | ❌ | IG wave generation |
| tp1.8 | ⏳ | 0 | 0 MB | ❌ | Wave breaking on beach |
| tp1.9 | ⏳ | 0 | 0 MB | ❌ | Nonlinear shoaling (triads) |
| tp1.10 | ⏳ | 0 | 0 MB | ❌ | Bottom scattering |

**Phase 1 Summary**: 0/10 tests with reference outputs

---

## Phase 2: tp2.x Tests (2-D Propagation)

| Test | Status | Files | Size | Checksum | Notes |
|------|--------|-------|------|----------|-------|
| tp2.1 | ⏳ | 0 | 0 MB | ❌ | 2-D propagation |
| tp2.2 | ⏳ | 0 | 0 MB | ❌ | Periodic boundary |
| tp2.3 | ⏳ | 0 | 0 MB | ❌ | Curvilinear grid |
| tp2.4 | ⏳ | 0 | 0 MB | ❌ | Great Lakes |
| tp2.5 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.6 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.7 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.8 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.9 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.10 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.11 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.12 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.13 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.14 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.15 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.16 | ⏳ | 0 | 0 MB | ❌ | TBD |
| tp2.17 | ⏳ | 0 | 0 MB | ❌ | TBD |

**Phase 2 Summary**: 0/17 tests with reference outputs

---

## Phase 3: mww3_test_xx (Multi-Grid)

*Deferred until ww3_multi component complete*

---

## Overall Summary

- **Total Tests Tracked**: 27
- **Reference Outputs Available**: 0 (0%)
- **Reference Outputs Pending**: 27 (100%)
- **Total Storage Used**: 0 MB
- **Estimated Total Storage**: ~10 GB

---

## Update Instructions

After generating reference outputs for a test:

1. **Update this file**:
   ```markdown
   | tp1.1 | ✅ | 25 | 5.2 MB | ✅ | Generated 2026-02-10 |
   ```

2. **Update status**:
   - Change ⏳ to ✅
   - Add file count
   - Add size in MB
   - Add checksum status (✅ if in CHECKSUMS.txt)
   - Add generation date or notes

3. **Update summary counts**:
   - Increment "Reference Outputs Available"
   - Decrement "Reference Outputs Pending"
   - Add size to "Total Storage Used"

4. **Commit changes**:
   ```bash
   git add regtests/reference_outputs/AVAILABLE_TESTS.md
   git add regtests/reference_outputs/CHECKSUMS.txt
   git commit -m "docs: add reference outputs for tp1.1"
   ```

---

## Validation Checklist

Before marking a test as ✅ Available:

- [ ] All expected output files present (NetCDF, point outputs)
- [ ] metadata.json created with WW3 version info
- [ ] Checksums added to CHECKSUMS.txt
- [ ] Checksum verification passes: `sha256sum -c CHECKSUMS.txt`
- [ ] File sizes reasonable (not corrupted)
- [ ] Test documented in this file

---

## Priority Tests for Reference Generation

Based on implementation status and test coverage:

**High Priority** (implemented, need references):
1. tp1.1 - Basic equatorial propagation
2. tp1.2 - Basic meridional propagation
3. tp1.3 - Monochromatic shoaling
4. tp2.4 - Great Lakes (already has rompy-ww3 implementation)

**Medium Priority** (implemented, advanced physics):
5. tp1.4 - Spectral refraction X
6. tp1.5 - Spectral refraction Y
7. tp1.6 - Wave-current interaction
8. tp1.7 - IG wave generation

**Lower Priority** (specialized physics):
9. tp1.8 - Wave breaking
10. tp1.9 - Triads
11. tp1.10 - Bottom scattering

---

## Notes

- Reference outputs are **NOT committed to git** (large binary files)
- Users must generate locally or download from external storage
- See README.md for generation and download instructions
- Checksums ensure integrity of downloaded/generated files

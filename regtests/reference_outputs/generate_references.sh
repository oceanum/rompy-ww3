#!/bin/bash
# generate_references.sh - Generate WW3 reference outputs for regression testing
#
# Usage:
#   ./generate_references.sh [options] <test_id> [<test_id> ...]
#
# Options:
#   --clean       Remove existing reference outputs before generating
#   --dry-run     Show commands without executing
#   --help        Show this help message
#
# Examples:
#   ./generate_references.sh tp1.1
#   ./generate_references.sh tp1  # All tp1.x tests
#   ./generate_references.sh --clean tp1.1 tp1.2
#   ./generate_references.sh --dry-run tp2.4

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGTESTS_DIR="$(dirname "$SCRIPT_DIR")"

# Options
CLEAN_MODE=false
DRY_RUN=false

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            grep '^#' "$0" | sed 's/^# //' | sed 's/^#//'
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# Check for test IDs
if [ $# -eq 0 ]; then
    echo -e "${RED}ERROR: No test IDs specified${NC}"
    echo "Usage: $0 [options] <test_id> [<test_id> ...]"
    echo "Try: $0 --help"
    exit 1
fi

# Expand test series (tp1 -> tp1.1 tp1.2 ... tp1.10)
TEST_IDS=()
for arg in "$@"; do
    if [[ "$arg" =~ ^tp[0-9]+$ ]]; then
        # Expand series (e.g., tp1 -> tp1.1 through tp1.10)
        series="${arg:2}"
        for i in {1..10}; do
            test_dir="$REGTESTS_DIR/ww3_tp${series}.$i"
            if [ -d "$test_dir" ]; then
                TEST_IDS+=("tp${series}.$i")
            fi
        done
    else
        TEST_IDS+=("$arg")
    fi
done

echo "==================================================================="
echo "WW3 Reference Output Generator"
echo "==================================================================="
echo ""
echo "Tests to process: ${TEST_IDS[*]}"
echo "Clean mode: $CLEAN_MODE"
echo "Dry run: $DRY_RUN"
echo ""

# Function to execute or print command
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] $*"
    else
        "$@"
    fi
}

# Function to check WW3 installation
check_ww3_installation() {
    echo "[1/6] Verifying WW3 installation..."
    
    if [ -z "$WW3_DIR" ]; then
        echo -e "${RED}ERROR: WW3_DIR environment variable not set${NC}"
        echo "Please set WW3_DIR to your WW3 installation directory"
        echo "Example: export WW3_DIR=/path/to/WW3"
        return 1
    fi
    
    if [ ! -d "$WW3_DIR" ]; then
        echo -e "${RED}ERROR: WW3_DIR directory does not exist: $WW3_DIR${NC}"
        return 1
    fi
    
    # Check for essential WW3 executables
    local required_exes=("ww3_grid" "ww3_shel" "ww3_ounf" "ww3_ounp")
    for exe in "${required_exes[@]}"; do
        if ! command -v "$exe" &> /dev/null && [ ! -f "$WW3_DIR/exe/$exe" ]; then
            echo -e "${YELLOW}WARNING: $exe not found in PATH or WW3_DIR/exe${NC}"
        fi
    done
    
    echo -e "${GREEN}OK${NC} - WW3_DIR: $WW3_DIR"
    return 0
}

# Function to get WW3 version
get_ww3_version() {
    if [ -d "$WW3_DIR/.git" ]; then
        cd "$WW3_DIR"
        local commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        local tag=$(git describe --tags --exact-match 2>/dev/null || echo "")
        cd - > /dev/null
        
        if [ -n "$tag" ]; then
            echo "$tag ($commit)"
        else
            echo "$commit"
        fi
    else
        echo "unknown (no git repository)"
    fi
}

# Function to generate reference for a single test
generate_reference() {
    local test_id=$1
    local test_dir="$REGTESTS_DIR/ww3_$test_id"
    local ref_dir="$SCRIPT_DIR/ww3_$test_id"
    
    echo ""
    echo "==================================================================="
    echo "Processing: $test_id"
    echo "==================================================================="
    
    # Check if test directory exists
    if [ ! -d "$test_dir" ]; then
        echo -e "${RED}ERROR: Test directory not found: $test_dir${NC}"
        return 1
    fi
    
    # Clean existing reference if requested
    if [ "$CLEAN_MODE" = true ] && [ -d "$ref_dir" ]; then
        echo "[2/6] Cleaning existing reference outputs..."
        run_cmd rm -rf "$ref_dir"
        echo -e "${GREEN}OK${NC} - Removed $ref_dir"
    fi
    
    # Create reference directory
    if [ ! -d "$ref_dir" ]; then
        run_cmd mkdir -p "$ref_dir"
    fi
    
    # Download input data
    echo "[3/6] Downloading input data..."
    if [ -d "$test_dir/input" ] && [ "$(ls -A "$test_dir/input" 2>/dev/null)" ]; then
        echo -e "${GREEN}OK${NC} - Input data already present"
    else
        run_cmd python "$REGTESTS_DIR/download_input_data.py" "$test_id"
    fi
    
    # Note: Steps 4-6 require actual WW3 execution
    # This is a placeholder for the full implementation
    
    echo "[4/6] Running WW3 model... ${YELLOW}(NOT IMPLEMENTED)${NC}"
    echo "      This requires:"
    echo "      - Compiling WW3 with appropriate switches"
    echo "      - Running ww3_grid to generate grid"
    echo "      - Running ww3_shel to execute model"
    echo "      - Running ww3_ounf/ww3_ounp for post-processing"
    echo ""
    echo "      For now, reference outputs must be generated manually"
    echo "      by running official WW3 regression tests and copying"
    echo "      output files to: $ref_dir"
    
    echo "[5/6] Copying output files... ${YELLOW}(MANUAL STEP REQUIRED)${NC}"
    echo "      After running official WW3 test, copy files:"
    echo "      - ww3.*.nc (NetCDF field output)"
    echo "      - tab*.ww3 (point output)"
    echo "      - *.spec (spectrum output)"
    echo "      - ww3_grid.out (grid preprocessing output)"
    
    echo "[6/6] Generating checksums and metadata... ${YELLOW}(DEFERRED)${NC}"
    
    # Create placeholder metadata
    if [ "$DRY_RUN" = false ]; then
        local ww3_version=$(get_ww3_version)
        cat > "$ref_dir/metadata.json" <<EOF
{
  "test_id": "ww3_$test_id",
  "status": "incomplete",
  "ww3_version": "$ww3_version",
  "generation_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "note": "Reference outputs must be generated by running official WW3 regression tests",
  "required_files": [
    "ww3.*.nc (NetCDF field output)",
    "tab*.ww3 (point output files)",
    "ww3_grid.out (grid preprocessing output)"
  ],
  "instructions": "See README.md for manual reference generation steps"
}
EOF
        echo -e "${YELLOW}INCOMPLETE${NC} - Metadata created: $ref_dir/metadata.json"
    fi
    
    echo ""
    echo -e "${YELLOW}⚠ NOTICE: Reference generation incomplete${NC}"
    echo "Reference outputs must be generated manually using official WW3."
    echo "See $SCRIPT_DIR/README.md for detailed instructions."
    echo ""
    
    return 0
}

# Main execution
echo "Checking WW3 installation..."
if ! check_ww3_installation; then
    echo -e "${RED}FAILED: WW3 installation check failed${NC}"
    echo ""
    echo "Reference outputs can still be generated manually."
    echo "See README.md for instructions."
fi

echo ""
echo "Processing ${#TEST_IDS[@]} test(s)..."

SUCCESS_COUNT=0
FAIL_COUNT=0

for test_id in "${TEST_IDS[@]}"; do
    if generate_reference "$test_id"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "==================================================================="
echo "Summary"
echo "==================================================================="
echo "Processed: ${#TEST_IDS[@]} test(s)"
echo "Success: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}WARNING: Some tests failed${NC}"
    exit 1
else
    echo -e "${GREEN}All tests processed successfully${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run official WW3 regression tests for: ${TEST_IDS[*]}"
    echo "2. Copy output files to reference_outputs/ww3_<test_id>/"
    echo "3. Run: ./update_checksums.sh to generate checksums"
    exit 0
fi

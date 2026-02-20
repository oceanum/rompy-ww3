"""
Comprehensive tests for enum parsing, JSON dumps, and namelist rendering.

Tests cover all 9 enum types:
- GRID_TYPE (str)
- COORD_TYPE (str)
- CLOS_TYPE (str)
- FORCING (str)
- IOSTYP (IntEnum)
- LayoutIndicator (IntEnum)
- FormatIndicator (IntEnum)
- HomogInputName (str)
- UpdateMethod (str)

Each test verifies:
1. Name/value normalization (exact, case-insensitive, numeric for IntEnum)
2. Invalid input rejection with proper error messages
3. JSON dump format (canonical values)
4. Namelist rendering output (canonical tokens)
5. Ambiguity handling
"""

import pytest
import json
from rompy_ww3.namelists.enums import (
    GRID_TYPE,
    COORD_TYPE,
    CLOS_TYPE,
    FORCING,
    IOSTYP,
    LayoutIndicator,
    FormatIndicator,
    HomogInputName,
    UpdateMethod,
    parse_enum,
)
from rompy_ww3.namelists import Domain, Grid, Input


# ============================================================================
# Part A: Name/value scalar normalization tests
# ============================================================================


class TestParseEnumNormalization:
    """Test parse_enum handles all input formats correctly."""

    def test_grid_type_exact_value(self):
        """Test exact value match for GRID_TYPE."""
        result = parse_enum(GRID_TYPE, "RECT")
        assert result == GRID_TYPE.RECT
        assert isinstance(result, GRID_TYPE)

    def test_grid_type_case_insensitive_value(self):
        """Test case-insensitive value match for GRID_TYPE."""
        result = parse_enum(GRID_TYPE, "rect")
        assert result == GRID_TYPE.RECT

    def test_grid_type_case_insensitive_name(self):
        """Test case-insensitive name match for GRID_TYPE."""
        result = parse_enum(GRID_TYPE, "rect")
        assert result == GRID_TYPE.RECT

    def test_grid_type_enum_member_passthrough(self):
        """Test enum member pass-through for GRID_TYPE."""
        result = parse_enum(GRID_TYPE, GRID_TYPE.RECT)
        assert result == GRID_TYPE.RECT

    def test_coord_type_all_values(self):
        """Test all COORD_TYPE values normalize correctly."""
        assert parse_enum(COORD_TYPE, "SPHE") == COORD_TYPE.SPHE
        assert parse_enum(COORD_TYPE, "sphe") == COORD_TYPE.SPHE
        assert parse_enum(COORD_TYPE, "CART") == COORD_TYPE.CART
        assert parse_enum(COORD_TYPE, "cart") == COORD_TYPE.CART

    def test_clos_type_all_values(self):
        """Test all CLOS_TYPE values normalize correctly."""
        assert parse_enum(CLOS_TYPE, "NONE") == CLOS_TYPE.NONE
        assert parse_enum(CLOS_TYPE, "none") == CLOS_TYPE.NONE
        assert parse_enum(CLOS_TYPE, "SMPL") == CLOS_TYPE.SMPL
        assert parse_enum(CLOS_TYPE, "smpl") == CLOS_TYPE.SMPL
        assert parse_enum(CLOS_TYPE, "TRPL") == CLOS_TYPE.TRPL
        assert parse_enum(CLOS_TYPE, "trpl") == CLOS_TYPE.TRPL

    def test_forcing_all_values(self):
        """Test all FORCING values normalize correctly."""
        assert parse_enum(FORCING, "F") == FORCING.F
        assert parse_enum(FORCING, "f") == FORCING.F
        assert parse_enum(FORCING, "T") == FORCING.T
        assert parse_enum(FORCING, "t") == FORCING.T
        assert parse_enum(FORCING, "H") == FORCING.H
        assert parse_enum(FORCING, "h") == FORCING.H
        assert parse_enum(FORCING, "C") == FORCING.C
        assert parse_enum(FORCING, "c") == FORCING.C

    def test_iostyp_integer_value(self):
        """Test integer value match for IOSTYP IntEnum."""
        assert parse_enum(IOSTYP, 0) == IOSTYP.TYPE0
        assert parse_enum(IOSTYP, 1) == IOSTYP.TYPE1
        assert parse_enum(IOSTYP, 2) == IOSTYP.TYPE2
        assert parse_enum(IOSTYP, 3) == IOSTYP.TYPE3

    def test_iostyp_numeric_string(self):
        """Test numeric string parsing for IOSTYP IntEnum."""
        assert parse_enum(IOSTYP, "0") == IOSTYP.TYPE0
        assert parse_enum(IOSTYP, "1") == IOSTYP.TYPE1
        assert parse_enum(IOSTYP, "2") == IOSTYP.TYPE2
        assert parse_enum(IOSTYP, "3") == IOSTYP.TYPE3

    def test_iostyp_name_match(self):
        """Test case-insensitive name match for IOSTYP."""
        assert parse_enum(IOSTYP, "TYPE0") == IOSTYP.TYPE0
        assert parse_enum(IOSTYP, "type1") == IOSTYP.TYPE1
        assert parse_enum(IOSTYP, "Type2") == IOSTYP.TYPE2

    def test_iostyp_enum_member_passthrough(self):
        """Test enum member pass-through for IOSTYP."""
        result = parse_enum(IOSTYP, IOSTYP.TYPE1)
        assert result == IOSTYP.TYPE1

    def test_layout_indicator_all_values(self):
        """Test all LayoutIndicator values normalize correctly."""
        assert parse_enum(LayoutIndicator, 1) == LayoutIndicator.LAYOUT_1
        assert parse_enum(LayoutIndicator, "1") == LayoutIndicator.LAYOUT_1
        assert parse_enum(LayoutIndicator, 2) == LayoutIndicator.LAYOUT_2
        assert parse_enum(LayoutIndicator, "2") == LayoutIndicator.LAYOUT_2
        assert parse_enum(LayoutIndicator, 3) == LayoutIndicator.LAYOUT_3
        assert parse_enum(LayoutIndicator, 4) == LayoutIndicator.LAYOUT_4

    def test_format_indicator_all_values(self):
        """Test all FormatIndicator values normalize correctly."""
        assert parse_enum(FormatIndicator, 1) == FormatIndicator.FREE_FORMAT
        assert parse_enum(FormatIndicator, "1") == FormatIndicator.FREE_FORMAT
        assert parse_enum(FormatIndicator, 2) == FormatIndicator.FIXED_FORMAT
        assert parse_enum(FormatIndicator, "2") == FormatIndicator.FIXED_FORMAT
        assert parse_enum(FormatIndicator, 3) == FormatIndicator.UNFORMATTED
        assert parse_enum(FormatIndicator, "3") == FormatIndicator.UNFORMATTED

    def test_homog_input_name_samples(self):
        """Test sample HomogInputName values normalize correctly."""
        assert parse_enum(HomogInputName, "IC1") == HomogInputName.IC1
        assert parse_enum(HomogInputName, "ic1") == HomogInputName.IC1
        assert parse_enum(HomogInputName, "WND") == HomogInputName.WND
        assert parse_enum(HomogInputName, "wnd") == HomogInputName.WND
        assert parse_enum(HomogInputName, "CUR") == HomogInputName.CUR
        assert parse_enum(HomogInputName, "RHO") == HomogInputName.RHO

    def test_update_method_all_values(self):
        """Test all UpdateMethod values normalize correctly."""
        assert parse_enum(UpdateMethod, "REPLACE") == UpdateMethod.REPLACE
        assert parse_enum(UpdateMethod, "replace") == UpdateMethod.REPLACE
        assert parse_enum(UpdateMethod, "ADD") == UpdateMethod.ADD
        assert parse_enum(UpdateMethod, "add") == UpdateMethod.ADD
        assert parse_enum(UpdateMethod, "MULTIPLY") == UpdateMethod.MULTIPLY
        assert parse_enum(UpdateMethod, "multiply") == UpdateMethod.MULTIPLY

    def test_whitespace_trimming(self):
        """Test that whitespace around strings is trimmed."""
        assert parse_enum(GRID_TYPE, "  RECT  ") == GRID_TYPE.RECT
        assert parse_enum(FORCING, " T ") == FORCING.T
        assert parse_enum(IOSTYP, " 1 ") == IOSTYP.TYPE1


# ============================================================================
# Part B: Invalid input rejection tests
# ============================================================================


class TestParseEnumInvalidInputs:
    """Test parse_enum raises ValueError with proper messages for invalid inputs."""

    def test_grid_type_invalid_string(self):
        """Test invalid string for GRID_TYPE raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(GRID_TYPE, "INVALID")
        assert "Invalid value" in str(exc_info.value)
        assert "RECT" in str(exc_info.value)
        assert "CURV" in str(exc_info.value)
        assert "UNST" in str(exc_info.value)
        assert "SMC" in str(exc_info.value)

    def test_coord_type_invalid_string(self):
        """Test invalid string for COORD_TYPE raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(COORD_TYPE, "POLAR")
        assert "Invalid value" in str(exc_info.value)
        assert "SPHE" in str(exc_info.value)
        assert "CART" in str(exc_info.value)

    def test_clos_type_invalid_string(self):
        """Test invalid string for CLOS_TYPE raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(CLOS_TYPE, "QUAD")
        assert "Invalid value" in str(exc_info.value)
        assert "NONE" in str(exc_info.value)
        assert "SMPL" in str(exc_info.value)
        assert "TRPL" in str(exc_info.value)

    def test_forcing_invalid_string(self):
        """Test invalid string for FORCING raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(FORCING, "X")
        assert "Invalid value" in str(exc_info.value)
        # Check that all valid values are listed
        error_msg = str(exc_info.value)
        assert "F" in error_msg
        assert "T" in error_msg
        assert "H" in error_msg
        assert "C" in error_msg

    def test_iostyp_invalid_integer(self):
        """Test invalid integer for IOSTYP raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(IOSTYP, 99)
        assert "Invalid value" in str(exc_info.value)
        error_msg = str(exc_info.value)
        assert "0" in error_msg
        assert "1" in error_msg
        assert "2" in error_msg
        assert "3" in error_msg

    def test_iostyp_invalid_numeric_string(self):
        """Test invalid numeric string for IOSTYP raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(IOSTYP, "99")
        assert "Invalid value" in str(exc_info.value)

    def test_layout_indicator_invalid_value(self):
        """Test invalid value for LayoutIndicator raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(LayoutIndicator, 99)
        assert "Invalid value" in str(exc_info.value)

    def test_format_indicator_invalid_value(self):
        """Test invalid value for FormatIndicator raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(FormatIndicator, 99)
        assert "Invalid value" in str(exc_info.value)

    def test_homog_input_name_invalid_string(self):
        """Test invalid string for HomogInputName raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(HomogInputName, "INVALID")
        assert "Invalid value" in str(exc_info.value)
        # Check some expected values are listed
        error_msg = str(exc_info.value)
        assert "IC1" in error_msg or "WND" in error_msg

    def test_update_method_invalid_string(self):
        """Test invalid string for UpdateMethod raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_enum(UpdateMethod, "INVALID")
        assert "Invalid value" in str(exc_info.value)
        error_msg = str(exc_info.value)
        assert "REPLACE" in error_msg
        assert "ADD" in error_msg
        assert "MULTIPLY" in error_msg


# ============================================================================
# Part C: JSON dumps emit canonical values
# ============================================================================


class TestJSONDumpsCanonicalValues:
    """Test that JSON serialization emits canonical enum values."""

    def test_domain_iostyp_json_dump(self):
        """Test Domain with IOSTYP serializes to integer value in JSON."""
        domain = Domain(iostyp=IOSTYP.TYPE1)
        json_str = domain.model_dump_json()
        data = json.loads(json_str)

        # Should contain integer value, not enum name or string representation
        assert data["iostyp"] == 1
        assert isinstance(data["iostyp"], int)
        # Should NOT contain "IOSTYP.TYPE1" or "TYPE1"
        assert "IOSTYP" not in json_str
        assert "TYPE1" not in json_str

    def test_domain_iostyp_from_string(self):
        """Test Domain accepts iostyp as numeric string."""
        domain = Domain(iostyp="1")
        assert domain.iostyp == IOSTYP.TYPE1
        json_str = domain.model_dump_json()
        data = json.loads(json_str)
        assert data["iostyp"] == 1

    def test_domain_iostyp_from_integer(self):
        """Test Domain accepts iostyp as integer."""
        domain = Domain(iostyp=2)
        assert domain.iostyp == IOSTYP.TYPE2
        json_str = domain.model_dump_json()
        data = json.loads(json_str)
        assert data["iostyp"] == 2

    def test_grid_type_json_dump(self):
        """Test Grid with GRID_TYPE serializes to string value in JSON."""
        grid = Grid(type=GRID_TYPE.RECT)
        json_str = grid.model_dump_json()
        data = json.loads(json_str)

        # Should contain canonical string value "RECT"
        assert data["type"] == "RECT"
        assert isinstance(data["type"], str)
        # Should NOT contain "GridType.RECT" or "GRID_TYPE.RECT"
        assert "GridType" not in json_str
        assert "GRID_TYPE" not in json_str

    def test_grid_coord_json_dump(self):
        """Test Grid with COORD_TYPE serializes to string value in JSON."""
        grid = Grid(coord=COORD_TYPE.SPHE)
        json_str = grid.model_dump_json()
        data = json.loads(json_str)

        assert data["coord"] == "SPHE"
        assert isinstance(data["coord"], str)
        assert "CoordType" not in json_str
        assert "COORD_TYPE" not in json_str

    def test_grid_clos_json_dump(self):
        """Test Grid with CLOS_TYPE serializes to string value in JSON."""
        grid = Grid(clos=CLOS_TYPE.SMPL)
        json_str = grid.model_dump_json()
        data = json.loads(json_str)

        assert data["clos"] == "SMPL"
        assert isinstance(data["clos"], str)
        assert "ClosType" not in json_str
        assert "CLOS_TYPE" not in json_str

    def test_input_forcing_json_dump(self):
        """Test Input with FORCING values serializes to string values in JSON."""
        input_nml = Input(forcing={"winds": FORCING.T, "currents": FORCING.F})
        json_str = input_nml.model_dump_json()
        data = json.loads(json_str)

        # Should contain canonical string values
        assert data["forcing"]["winds"] == "T"
        assert data["forcing"]["currents"] == "F"
        # Should NOT contain "FORCING.T" or "FORCING.F"
        assert "FORCING" not in json_str

    def test_grid_case_insensitive_input_json_dump(self):
        """Test Grid accepts case-insensitive input and serializes correctly."""
        grid = Grid(type="rect", coord="sphe", clos="smpl")
        json_str = grid.model_dump_json()
        data = json.loads(json_str)

        # Should normalize to canonical uppercase values
        assert data["type"] == "RECT"
        assert data["coord"] == "SPHE"
        assert data["clos"] == "SMPL"


# ============================================================================
# Part D: Namelist rendering uses canonical tokens
# ============================================================================


class TestNamelistRenderingCanonicalTokens:
    """Test that namelist rendering outputs canonical WW3 tokens."""

    def test_domain_iostyp_rendering(self):
        """Test Domain with IOSTYP renders integer value."""
        domain = Domain(iostyp=IOSTYP.TYPE1)
        rendered = domain.render()

        # Should contain "IOSTYP = 1" not "IOSTYP = TYPE1" or "IOSTYP = IOSTYP.TYPE1"
        assert "IOSTYP = 1" in rendered or "IOSTYP=1" in rendered
        assert "TYPE1" not in rendered
        assert "IOSTYP.TYPE1" not in rendered

    def test_domain_iostyp_from_string_rendering(self):
        """Test Domain with iostyp from string renders correctly."""
        domain = Domain(iostyp="2")
        rendered = domain.render()

        assert "IOSTYP = 2" in rendered or "IOSTYP=2" in rendered

    def test_grid_type_rendering(self):
        """Test Grid type field renders canonical value."""
        grid = Grid(type=GRID_TYPE.RECT)
        rendered = grid.render()

        # Should contain "GRID%TYPE = 'RECT'" not "GRID%TYPE = 'GridType.RECT'"
        assert "RECT" in rendered
        assert "GridType" not in rendered
        assert "GRID_TYPE" not in rendered

    def test_grid_type_case_insensitive_rendering(self):
        """Test Grid with case-insensitive input renders canonical value."""
        grid = Grid(type="rect")
        rendered = grid.render()

        # Should normalize to uppercase canonical value
        assert "RECT" in rendered

    def test_grid_coord_rendering(self):
        """Test Grid coord field renders canonical value."""
        grid = Grid(coord=COORD_TYPE.SPHE)
        rendered = grid.render()

        assert "SPHE" in rendered
        assert "CoordType" not in rendered

    def test_grid_clos_rendering(self):
        """Test Grid clos field renders canonical value."""
        grid = Grid(clos=CLOS_TYPE.SMPL)
        rendered = grid.render()

        assert "SMPL" in rendered
        assert "ClosType" not in rendered

    def test_input_forcing_rendering(self):
        """Test Input forcing fields render canonical values."""
        input_nml = Input(forcing={"winds": FORCING.T, "water_levels": FORCING.F})
        rendered = input_nml.render()

        # Should contain canonical 'T' and 'F' values
        assert "'T'" in rendered or "= T" in rendered
        assert "'F'" in rendered or "= F" in rendered
        # Should NOT contain "FORCING.T" or "FORCING.F"
        assert "FORCING.T" not in rendered
        assert "FORCING.F" not in rendered

    def test_input_forcing_case_insensitive_rendering(self):
        """Test Input with case-insensitive forcing renders canonical values."""
        input_nml = Input(forcing={"winds": "t", "currents": "f"})
        rendered = input_nml.render()

        # Should normalize to uppercase canonical values
        assert "'T'" in rendered or "= T" in rendered
        assert "'F'" in rendered or "= F" in rendered


# ============================================================================
# Part E: Ambiguity handling
# ============================================================================


class TestAmbiguityHandling:
    """Test that parse_enum handles ambiguity correctly.

    With current enums, there should be no ambiguity issues since all
    enum members have unique names and values. This documents the behavior.
    """

    def test_no_ambiguity_in_current_enums(self):
        """Verify current enums have no ambiguous values."""
        # Check that each enum has unique values
        grid_values = [e.value for e in GRID_TYPE]
        assert len(grid_values) == len(set(grid_values))

        coord_values = [e.value for e in COORD_TYPE]
        assert len(coord_values) == len(set(coord_values))

        clos_values = [e.value for e in CLOS_TYPE]
        assert len(clos_values) == len(set(clos_values))

        forcing_values = [e.value for e in FORCING]
        assert len(forcing_values) == len(set(forcing_values))

        iostyp_values = [e.value for e in IOSTYP]
        assert len(iostyp_values) == len(set(iostyp_values))

    def test_parse_enum_precedence(self):
        """Test that parse_enum follows documented precedence rules.

        1. Enum instance passthrough
        2. Exact value match
        3. Case-insensitive value match
        4. Case-insensitive name match
        5. IntEnum numeric string parsing
        """
        # Test 1: Enum instance passthrough
        result = parse_enum(GRID_TYPE, GRID_TYPE.RECT)
        assert result is GRID_TYPE.RECT

        # Test 2: Exact value match
        result = parse_enum(GRID_TYPE, "RECT")
        assert result == GRID_TYPE.RECT

        # Test 3: Case-insensitive value match
        result = parse_enum(GRID_TYPE, "rect")
        assert result == GRID_TYPE.RECT

        # Test 5: IntEnum numeric string parsing
        result = parse_enum(IOSTYP, "1")
        assert result == IOSTYP.TYPE1


# ============================================================================
# Part F: Integration tests with actual namelist classes
# ============================================================================


class TestNamelistIntegration:
    """Test enum integration with actual namelist classes."""

    def test_domain_accepts_integer(self):
        """Test Domain(iostyp=1) accepts integer."""
        domain = Domain(iostyp=1)
        assert domain.iostyp == IOSTYP.TYPE1

    def test_domain_accepts_numeric_string(self):
        """Test Domain(iostyp='1') accepts numeric string."""
        domain = Domain(iostyp="1")
        assert domain.iostyp == IOSTYP.TYPE1

    def test_domain_accepts_enum_member(self):
        """Test Domain(iostyp=IOSTYP.TYPE1) accepts enum member."""
        domain = Domain(iostyp=IOSTYP.TYPE1)
        assert domain.iostyp == IOSTYP.TYPE1

    def test_domain_rejects_invalid_iostyp(self):
        """Test Domain rejects invalid iostyp value."""
        with pytest.raises(ValueError) as exc_info:
            Domain(iostyp=99)
        assert "Invalid value" in str(exc_info.value)

    def test_grid_accepts_case_insensitive_type(self):
        """Test Grid(type='rect') accepts case-insensitive string."""
        grid = Grid(type="rect")
        assert grid.type == GRID_TYPE.RECT

    def test_grid_accepts_case_insensitive_coord(self):
        """Test Grid(coord='sphe') accepts case-insensitive string."""
        grid = Grid(coord="sphe")
        assert grid.coord == COORD_TYPE.SPHE

    def test_grid_accepts_canonical_values(self):
        """Test Grid accepts canonical values directly."""
        grid = Grid(type="RECT", coord="SPHE", clos="SMPL")
        assert grid.type == GRID_TYPE.RECT
        assert grid.coord == COORD_TYPE.SPHE
        assert grid.clos == CLOS_TYPE.SMPL

    def test_grid_accepts_enum_members(self):
        """Test Grid accepts enum members directly."""
        grid = Grid(type=GRID_TYPE.CURV, coord=COORD_TYPE.CART, clos=CLOS_TYPE.NONE)
        assert grid.type == GRID_TYPE.CURV
        assert grid.coord == COORD_TYPE.CART
        assert grid.clos == CLOS_TYPE.NONE

    def test_grid_rejects_invalid_type(self):
        """Test Grid rejects invalid type value."""
        with pytest.raises(ValueError) as exc_info:
            Grid(type="INVALID")
        assert "Invalid value" in str(exc_info.value)

    def test_grid_rejects_invalid_coord(self):
        """Test Grid rejects invalid coord value."""
        with pytest.raises(ValueError) as exc_info:
            Grid(coord="POLAR")
        assert "Invalid value" in str(exc_info.value)

    def test_grid_rejects_invalid_clos(self):
        """Test Grid rejects invalid clos value."""
        with pytest.raises(ValueError) as exc_info:
            Grid(clos="INVALID")
        assert "Invalid value" in str(exc_info.value)

    def test_input_accepts_case_insensitive_forcing(self):
        """Test Input accepts case-insensitive forcing values."""
        input_nml = Input(forcing={"winds": "t", "currents": "f"})
        assert input_nml.forcing.winds == FORCING.T
        assert input_nml.forcing.currents == FORCING.F

    def test_input_accepts_enum_forcing(self):
        """Test Input accepts enum members for forcing."""
        input_nml = Input(forcing={"winds": FORCING.H, "currents": FORCING.C})
        assert input_nml.forcing.winds == FORCING.H
        assert input_nml.forcing.currents == FORCING.C

    def test_input_rejects_invalid_forcing(self):
        """Test Input rejects invalid forcing value."""
        with pytest.raises(ValueError) as exc_info:
            Input(forcing={"winds": "INVALID"})
        assert "Invalid value" in str(exc_info.value)

    def test_complete_domain_with_enums(self):
        """Test complete Domain creation with enum values."""
        from datetime import datetime

        domain = Domain(
            start=datetime(2023, 1, 1),
            stop=datetime(2023, 1, 7),
            iostyp=1,  # Accepts integer, converts to enum
        )
        assert domain.iostyp == IOSTYP.TYPE1

        # Verify rendering works
        rendered = domain.render()
        assert "&DOMAIN_NML" in rendered
        assert "IOSTYP = 1" in rendered or "IOSTYP=1" in rendered

    def test_complete_grid_with_enums(self):
        """Test complete Grid creation with enum values."""
        grid = Grid(
            name="test_grid",
            type="rect",  # Case-insensitive string
            coord="SPHE",  # Canonical value
            clos=CLOS_TYPE.SMPL,  # Enum member
            zlim=-0.1,
            dmin=2.5,
        )
        assert grid.type == GRID_TYPE.RECT
        assert grid.coord == COORD_TYPE.SPHE
        assert grid.clos == CLOS_TYPE.SMPL

        # Verify rendering works
        rendered = grid.render()
        assert "&GRID_NML" in rendered
        assert "RECT" in rendered
        assert "SPHE" in rendered
        assert "SMPL" in rendered


# ============================================================================
# Summary test to verify all enum types are covered
# ============================================================================


def test_all_enum_types_covered():
    """Verify that all 9 enum types are tested."""
    tested_enums = [
        GRID_TYPE,
        COORD_TYPE,
        CLOS_TYPE,
        FORCING,
        IOSTYP,
        LayoutIndicator,
        FormatIndicator,
        HomogInputName,
        UpdateMethod,
    ]

    # Verify we can parse at least one value from each enum
    test_values = [
        (GRID_TYPE, "RECT"),
        (COORD_TYPE, "SPHE"),
        (CLOS_TYPE, "NONE"),
        (FORCING, "T"),
        (IOSTYP, 1),
        (LayoutIndicator, 1),
        (FormatIndicator, 1),
        (HomogInputName, "WND"),
        (UpdateMethod, "REPLACE"),
    ]

    for enum_cls, test_val in test_values:
        result = parse_enum(enum_cls, test_val)
        assert isinstance(result, enum_cls)

    print(f"\n✓ All {len(tested_enums)} enum types tested successfully")

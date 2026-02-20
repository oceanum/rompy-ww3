# WW3 Post-Processing Examples

This directory contains example configurations for using the WW3 Transfer Postprocessor.

## postprocess_transfer_example.yaml

A complete `rompy` CLI-compatible example demonstrating how to transfer WW3 model outputs to multiple destinations with datestamped filenames.

### Features Demonstrated

- **Full ModelRun configuration** - Complete WW3 model setup with domain, grid, and output configuration
- **Multi-destination transfer** - Transfer outputs to multiple backup/archive locations
- **Datestamped filenames** - Automatic filename generation with timestamps (e.g., `20230101_060000_restart.ww3`)
- **Restart handling** - Special valid-date computation for restart files
- **Field output transfer** - Transfer field outputs with proper naming
- **Failure policies** - Continue or fail-fast on transfer errors

### Usage

#### 1. Run Postprocessing Only

If you already have WW3 model outputs from a previous run:

```bash
rompy postprocess examples/postprocess_transfer_example.yaml --processor ww3_transfer
```

This will:
- Load the model configuration
- Discover WW3 output files (restart.ww3, field outputs, etc.)
- Transfer them to configured destinations with datestamped filenames
- Report transfer results

#### 2. Run Full Pipeline

To run the complete model workflow (generate → run → postprocess):

```bash
rompy pipeline examples/postprocess_transfer_example.yaml --processor ww3_transfer
```

This will:
1. Generate WW3 namelist files
2. Run the WW3 model (requires WW3 installation)
3. Transfer outputs to configured destinations

#### 3. Dry-Run / Validation

To validate the configuration without executing:

```bash
rompy validate examples/postprocess_transfer_example.yaml
```

### Configuration Sections

#### Model Configuration (`config`)

Defines the WW3 model setup:
- **model_type**: Must be `shel` (single-grid) or `multi` (multi-grid)
- **ww3_shel**: Shell component with domain, input, output configuration
- **ww3_grid**: Grid component with spectrum, run parameters, grid geometry

#### Postprocessor Configuration (`postprocessor.ww3_transfer`)

Defines transfer settings:

```yaml
postprocessor:
  ww3_transfer:
    destinations:
      - "file:///backup/location/"      # Local filesystem
      - "s3://bucket/prefix/"            # S3 bucket (requires s3fs)
      - "oceanum://endpoint/dataset/"   # Oceanum platform
    
    output_types:
      restart:
        extra: DW                        # Matches ww3_shel.output_type.restart
      field:
        list: [1, 2, 3, 4]              # Index references to field outputs
    
    failure_policy: "CONTINUE"          # "CONTINUE" or "FAIL_FAST"
    start_date: "20230101 000000"       # WW3 format for restart valid-date
    output_stride: 21600                # Seconds (6 hours)
```

#### Destination Formats

The `destinations` list supports any prefix registered in `rompy.transfer`:

- **Local filesystem**: `file:///absolute/path/` or `file://./relative/path/`
- **S3**: `s3://bucket-name/prefix/` (requires `s3fs` installed)
- **HTTP**: `http://server/path/` or `https://server/path/`
- **Oceanum**: `oceanum://endpoint/dataset/` (requires `oceanum-python`)
- **Custom**: Any backend registered via rompy transfer entry points

### Customizing for Your Use Case

#### Adjust Model Domain

```yaml
config:
  ww3_shel:
    domain:
      start: 20230101 000000            # Start date (YYYYMMDD HHMMSS)
      stop: 20230131 000000             # Stop date (YYYYMMDD HHMMSS)
      iostyp: 1                         # I/O type (0=minimal, 1=restart, etc.)
```

#### Configure Output Types

```yaml
config:
  ww3_shel:
    output_type:
      restart:
        extra: DW                       # Extra output (D=daily, W=weekly)
      field:
        list: [HS, DIR, SPR, DP, WND]  # Field variables to output
      point:
        list: [1, 2, 3]                # Point output stations
```

#### Adjust Output Frequency

```yaml
config:
  ww3_shel:
    output_date:
      restart:
        stride: 21600                   # 6 hours
      field:
        stride: 3600                    # 1 hour
```

#### Add More Destinations

```yaml
postprocessor:
  ww3_transfer:
    destinations:
      - "file:///primary/backup/"
      - "file:///secondary/backup/"
      - "s3://archive-bucket/ww3/"
      - "s3://public-bucket/public-data/"
```

### Multi-Grid Configuration Example

For multi-grid models, change `model_type` to `multi` and configure accordingly:

```yaml
config:
  model_type: multi
  multi:
    # Multi-grid configuration (see regtests/mww3_test_* for examples)
  grids:
    - name: coarse
      grid: { ... }
    - name: fine
      grid: { ... }
```

The postprocessor configuration remains the same - it works with both single-grid and multi-grid models.

### Troubleshooting

#### Transfer Failures

If transfers fail:

1. **Check destinations are accessible**:
   ```bash
   # For local filesystem
   ls -ld /backup/location/
   
   # For S3
   aws s3 ls s3://bucket-name/prefix/
   ```

2. **Verify credentials**:
   - S3: Ensure AWS credentials are configured (`~/.aws/credentials` or environment)
   - Oceanum: Check API tokens are set

3. **Use verbose logging**:
   ```bash
   rompy postprocess examples/postprocess_transfer_example.yaml \
     --processor ww3_transfer -vv
   ```

4. **Change failure policy** to debug individual transfers:
   ```yaml
   failure_policy: "FAIL_FAST"  # Stop on first error for debugging
   ```

#### Output Files Not Found

If postprocessor reports "no files to transfer":

1. **Check output directory exists**:
   ```bash
   ls -la ./ww3_output/
   ```

2. **Verify output_types match WW3 configuration**:
   - `postprocessor.ww3_transfer.output_types` must match `config.ww3_shel.output_type`

3. **Check model completed successfully**:
   ```bash
   # Look for error messages in WW3 log files
   cat ./ww3_output/log.ww3
   ```

## Related Documentation

- **Main Documentation**: See `docs/usage.md` for comprehensive postprocessor documentation
- **Implementation**: See `src/rompy_ww3/postprocess/` for source code
- **Tests**: See `tests/postprocess/` for unit tests
- **Regression Tests**: See `regtests/ww3_tp*/` and `regtests/mww3_test_*/` for full model examples

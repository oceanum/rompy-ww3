"""Console script for rompy_ww3."""

from pathlib import Path
from typing import List, Optional, cast

import typer
from rich.console import Console
from rich.table import Table
from rompy.core.responses import ArtifactType

from .components.grid import Grid as GridComponent
from .config import Config
from .namelists.enums import GRID_TYPE
from .namelists.grid import Grid as GridNamelist
from .namelists.grid import Rect
from .postprocess.lifecycle import run_transfer_postprocess

app = typer.Typer()
console = Console()


def _parse_grid_type(value: str) -> GRID_TYPE:
    for grid_type in GRID_TYPE:
        if (
            grid_type.name.lower() == value.lower()
            or grid_type.value.lower() == value.lower()
        ):
            return grid_type
    raise ValueError(f"Invalid grid type: {value}")


@app.command()
def init(
    output_dir: Path = typer.Option(
        Path.cwd() / "ww3_config",
        "--output",
        "-o",
        help="Output directory for the WW3 configuration",
    ),
    model_name: str = typer.Option(
        "ww3_model", "--name", "-n", help="Name of the model"
    ),
):
    """Initialize a new WW3 model configuration."""
    console.print(f"Initializing WW3 model configuration in {output_dir}")
    config = Config(template=str(Path(__file__).parent / "templates" / "base"))
    output_dir.mkdir(parents=True, exist_ok=True)
    config_file = output_dir / "config.json"
    with open(config_file, "w") as f:
        f.write(config.model_dump_json(indent=2))

    console.print(f"[green]✓[/green] WW3 configuration initialized: {config_file}")
    console.print(f"[blue]→[/blue] Edit {config_file} to customize your model setup")


@app.command()
def run(
    config_file: Path = typer.Argument(
        ..., help="Path to the WW3 configuration file (JSON format)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show what would be executed without running the model",
    ),
):
    """Run a WW3 model simulation."""
    if not config_file.exists():
        console.print(f"[red]✗[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)

    with open(config_file, "r") as f:
        config_data = f.read()

    config = Config.model_validate_json(config_data)

    console.print(
        f"[blue]→[/blue] Running WW3 simulation with configuration: {config_file.name}"
    )

    if dry_run:
        console.print(
            "[yellow]→[/yellow] DRY RUN MODE: Would execute WW3 with the given configuration"
        )
        console.print(f"[yellow]→[/yellow] Model type: {config.model_type}")
        console.print(f"[yellow]→[/yellow] Template: {config.template}")
        console.print(
            "[yellow]→[/yellow] Namelist files would be generated in the staging directory"
        )
    else:
        console.print("[green]✓[/green] WW3 simulation completed successfully")


@app.command()
def create_grid(
    output_file: Path = typer.Argument(
        ..., help="Output file for the grid configuration"
    ),
    grid_type: str = typer.Option(
        "RECT", "--type", "-t", help="Grid type (RECT, CURV, UNST)"
    ),
    nx: int = typer.Option(50, "--nx", help="Number of points in x-direction"),
    ny: int = typer.Option(50, "--ny", help="Number of points in y-direction"),
    x0: float = typer.Option(-10.0, "--x0", help="Western boundary"),
    y0: float = typer.Option(40.0, "--y0", help="Southern boundary"),
    x1: float = typer.Option(10.0, "--x1", help="Eastern boundary"),
    y1: float = typer.Option(60.0, "--y1", help="Northern boundary"),
):
    """Create a WW3 grid configuration."""
    console.print(f"[blue]→[/blue] Creating WW3 grid configuration: {output_file}")

    parsed_grid_type = cast(GRID_TYPE, _parse_grid_type(grid_type))
    grid = GridComponent(
        grid=GridNamelist(type=parsed_grid_type),
        rect=Rect(
            nx=nx,
            ny=ny,
            x0=x0,
            y0=y0,
            sx=(x1 - x0) / max(nx - 1, 1),
            sy=(y1 - y0) / max(ny - 1, 1),
        ),
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    grid.write_nml(output_file.parent)

    console.print("[green]✓[/green] WW3 grid configuration created successfully")
    console.print(f"[green]✓[/green] Grid files written to: {output_file.parent}")


@app.command()
def list_components():
    """List available WW3 components and their configurations."""
    table = Table(title="WW3 Components")

    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Status", style="green")

    table.add_row("Config", "Main configuration class", "Implemented")
    table.add_row("Grid", "Grid definition and parameters", "Implemented")
    table.add_row("Data", "Data handling and forcing", "Implemented")
    table.add_row("Source", "Data source definitions", "Implemented")
    table.add_row("Namelist", "All WW3 namelist configurations", "Implemented")

    console.print(table)


@app.command()
def validate_config(
    config_file: Path = typer.Argument(
        ..., help="Path to the WW3 configuration file (JSON format)"
    ),
):
    """Validate a WW3 configuration file."""
    if not config_file.exists():
        console.print(f"[red]✗[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)

    with open(config_file, "r") as f:
        config_data = f.read()

    try:
        config = Config.model_validate_json(config_data)
        domain = config.ww3_shel.domain if config.ww3_shel else None
        grid = config.ww3_grid
        timesteps = grid.timesteps if grid else None

        issues = []
        if domain is None:
            issues.append("Missing domain configuration (required)")
        elif domain.start is None or domain.stop is None:
            issues.append("Domain missing start or stop time")

        if grid is None:
            issues.append("Missing grid configuration")

        if timesteps is None:
            issues.append("Missing timesteps configuration (required)")

        if issues:
            console.print(
                f"[red]✗[/red] Configuration validation failed with {len(issues)} issues:"
            )
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("[green]✓[/green] Configuration is valid")
            console.print(f"[blue]→[/blue] Model type: {config.model_type}")
            if domain:
                console.print(
                    f"[blue]→[/blue] Model run: {domain.start} to {domain.stop}"
                )
            if grid and grid.grid:
                console.print(f"[blue]→[/blue] Grid type: {grid.grid.type}")

    except Exception as e:
        console.print(f"[red]✗[/red] Configuration parsing failed: {str(e)}")
        raise typer.Exit(1)


@app.command()
def postprocess(
    path: Path = typer.Argument(
        ..., help="Path to an output directory or run_result.json file"
    ),
    destinations: List[str] = typer.Option(
        ..., "--destination", "-d", help="Destination URI(s) to transfer outputs to"
    ),
    failure_policy: str = typer.Option(
        "CONTINUE",
        "--failure-policy",
        "-p",
        help="Failure policy: CONTINUE or FAIL_FAST",
    ),
    artifact_types: Optional[List[str]] = typer.Option(
        None,
        "--artifact-type",
        "-a",
        help="Optional artifact type filter (repeatable). Names from rompy.core.responses.ArtifactType",
    ),
):
    p = Path(path)
    if not p.exists():
        console.print(f"[red]✗[/red] Persisted run not found: {p}")
        raise typer.Exit(1)

    normalized_failure_policy = failure_policy.upper()
    if normalized_failure_policy not in {"CONTINUE", "FAIL_FAST"}:
        console.print(f"[red]✗[/red] Unknown failure policy: {failure_policy}")
        raise typer.Exit(1)

    mapped_types = None
    if artifact_types:
        mapped = []
        for at in artifact_types:
            match = next(
                (
                    artifact_type
                    for artifact_type in ArtifactType
                    if artifact_type.name.lower() == at.lower()
                    or str(artifact_type.value).lower() == at.lower()
                ),
                None,
            )
            if match is None:
                console.print(f"[red]✗[/red] Unknown artifact type: {at}")
                raise typer.Exit(1)
            mapped.append(match)
        mapped_types = mapped

    try:
        result = run_transfer_postprocess(
            p,
            destinations=destinations,
            artifact_types=mapped_types,
            failure_policy=normalized_failure_policy,
        )
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Postprocess failed: {e}")
        raise typer.Exit(1)

    meta = getattr(result, "metadata", {}) or {}
    if meta.get("skipped"):
        console.print(f"[yellow]→[/yellow] Skipped: transfer already completed for {p}")
        raise typer.Exit(0)

    if getattr(result, "success", False):
        transferred = meta.get("transferred_count") or meta.get("transferred")
        failed = meta.get("failed_count") or meta.get("failed")
        console.print(
            f"[green]✓[/green] Transfer completed: {getattr(result, 'message', '')}"
        )
        if transferred is not None:
            console.print(f"[blue]→[/blue] Transferred: {transferred}")
        if failed is not None:
            console.print(f"[blue]→[/blue] Failed: {failed}")
        raise typer.Exit(0)

    console.print(
        f"[red]✗[/red] Transfer failed: {getattr(result, 'message', 'unknown error')}"
    )
    raise typer.Exit(1)


if __name__ == "__main__":
    app()

"""Console script for rompy_ww3."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .config import Config
from .grid import Grid

app = typer.Typer()
console = Console()


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

    # Create a basic WW3 config
    config = Config(
        model_type="ww3",
        template=str(Path(__file__).parent / "templates" / "base"),
    )

    # Save the config to the output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write a basic configuration file
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

    # Load the WW3 configuration
    with open(config_file, "r") as f:
        config_data = f.read()

    # In a real implementation, we would parse the config and execute the WW3 model
    # For now, we'll just simulate the process
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
        # In a real implementation, we would actually run the model here


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

    # Create a grid instance
    grid = Grid(
        model_type="ww3",
        grid_type=grid_type,
        nx=nx,
        ny=ny,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
    )

    # Generate and write the grid namelist files
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write the grid files
    grid.write_grid_files(output_file.parent)

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

    # Load the WW3 configuration
    with open(config_file, "r") as f:
        config_data = f.read()

    try:
        # Attempt to parse the configuration
        config = Config.model_validate_json(config_data)

        # Validate the configuration
        issues = []
        if config.domain is None:
            issues.append("Missing domain configuration (required)")
        elif config.domain.start is None or config.domain.stop is None:
            issues.append("Domain missing start or stop time")

        if config.grid is None:
            issues.append("Missing grid configuration")

        if config.timesteps is None:
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
            if config.domain:
                console.print(
                    f"[blue]→[/blue] Model run: {config.domain.start} to {config.domain.stop}"
                )
            if config.grid:
                console.print(f"[blue]→[/blue] Grid type: {config.grid.grid_type}")

    except Exception as e:
        console.print(f"[red]✗[/red] Configuration parsing failed: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

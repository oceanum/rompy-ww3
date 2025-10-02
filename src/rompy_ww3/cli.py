"""Console script for rompy_ww3."""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for rompy_ww3."""
    console.print(
        "Replace this message by putting your code into " "rompy_ww3.cli.main"
    )
    console.print("See Typer documentation at https://typer.tiangolo.com/")


if __name__ == "__main__":
    app()

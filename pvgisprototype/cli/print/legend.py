from rich.table import Table
from math import ceil
from pvgisprototype.constants import (
    SYMBOL_DESCRIPTIONS,
    SYMBOL_LOSS_NAME,
    SYMBOL_MEAN,
    SYMBOL_MEAN_NAME,
    SYMBOL_POWER_NAME,
    SYMBOL_SUMMATION,
    SYMBOL_SUMMATION_NAME,
)


def build_legend_table(
    dictionary: dict,
    caption: str,
    show_sum: bool = False,
    show_mean: bool = False,
    show_header: bool = False,
    box: str | None = None,  # box=SIMPLE_HEAD,
):
    """
    """
    # first : Identify symbols in the input dictionary
    filtered_symbols = {
        symbol: description
        for symbol, description in SYMBOL_DESCRIPTIONS.items()
        if any(symbol in key for key in dictionary.keys())
    }
    # Check for SYMBOL_SUMMATION in the input dictionary before adding
    if show_sum or any(SYMBOL_SUMMATION in key for key in dictionary.keys()):
        filtered_symbols[SYMBOL_SUMMATION] = f"[purple]{SYMBOL_SUMMATION_NAME}[/purple]"

    # Check for SYMBOL_MEAN in the input dictionary before adding
    if show_mean or any(SYMBOL_MEAN in key for key in dictionary.keys()):
        filtered_symbols[SYMBOL_MEAN] = f"[blue]{SYMBOL_MEAN_NAME}[/blue]"

    # then : Create a Legend table for the symbols in question
    legend = Table(
        # title='Legend',
        # title="[code]Legend[/code]",
        # caption="Caption text",
        show_header=show_header,
        # header_style="dim",
        # row_styles=["none", "dim"],
        box=box,
        # highlight=True,
        # pad_edge=False,
        # collapse_padding=True,
    )

    # next : Determine the number of columns based on the "height" of Caption 
    if len(caption.splitlines()) == 0:
        return None
    else:
        number_of_symbols = len(filtered_symbols)
        number_of_rows = len(caption.splitlines())
        number_of_columns = ceil(number_of_symbols / number_of_rows) * 2  # Multiply by 2 for Symbol & Description pairs
        for _ in range(number_of_columns // 2):
            legend.add_column("Symbol", justify="center", style="bold blue", no_wrap=True)
            legend.add_column("Description", justify="left", style="dim", no_wrap=False)

        # finally : Populate the Legend table row by row
        rows = [["" for _ in range(number_of_columns)] for _ in range(number_of_rows)]  # Empty table grid
        current_row = 0  # Start with the first row
        current_column = 0  # Start with the first column pair

        for symbol, description in filtered_symbols.items():
            print(f"{symbol=} and {description=}")
            rows[current_row][current_column * 2] = f"[yellow]{symbol}[/yellow]"  # Symbol column
            if description == SYMBOL_POWER_NAME:
                rows[current_row][current_column * 2 + 1] = f"[dark_orange]{description}[/dark_orange]"  # Description column
            elif description == SYMBOL_LOSS_NAME:
                rows[current_row][current_column * 2 + 1] = f"[red bold]{description}[/red bold]"  # Description column
            else:
                rows[current_row][current_column * 2 + 1] = description  # Description column

            current_row += 1
            if current_row >= number_of_rows:  # Move to the next column if rows are filled
                current_row = 0
                current_column += 1

        # Add rows to the legend table
        for row in rows:
            legend.add_row(*row)

        return legend

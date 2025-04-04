from pvgisprototype.constants import SYMBOL_GROUPS_DESCRIPTIONS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.box import SIMPLE_HEAD
from rich import box


def create_symbol_group_table(category, symbols):
    table = Table(title=category, box=box.SIMPLE, show_header=True, header_style="bold magenta")
    table.add_column("Symbol", style="bright_blue", no_wrap=True)
    table.add_column("Description", style="cyan")

    for symbol, description in symbols.items():
        table.add_row(symbol, description)
    return table


def create_panel_for_table(table):
    return Panel(table, expand=False)


def create_symbols_table():
    """
    """
    main_table = Table(
        title='Symbol Descriptions',
        caption='This table categorizes different symbols used throughout the system.',
        show_header=False,
        box=SIMPLE_HEAD,
        highlight=True,
    )
    for category, symbols in SYMBOL_GROUPS_DESCRIPTIONS.items():
        category_table = Table(box=SIMPLE_HEAD)
        category_table.add_column("Symbol", justify="right", style="bright_blue", no_wrap=True)
        category_table.add_column("Description", style="cyan")

        for symbol, description in symbols.items():
            category_table.add_row(f'[bold]{symbol}[/bold]', description)

        main_table.add_row(category)
        main_table.add_row(category_table)
        main_table.add_row("")

    return main_table


def layout_panels_with_categories(symbol_group_descriptions):
    console = Console(record=True) 
    panels = []

    for category, symbols in symbol_group_descriptions.items():
        table = create_symbol_group_table(category, symbols)
        panel = create_panel_for_table(table)
        panels.append(panel)

    # Organize panels into columns
    # columns = Columns(panels, expand=True, equal=True, padding=1)
    columns = Columns(panels, padding=1)
    return columns


def print_pvgis_symbols():
    """
    """
    # console = Console(record=True, width=150)
    console = Console()
    # console.print(create_symbols_table(), markup=True, highlight=False)
    panels = layout_panels_with_categories(SYMBOL_GROUPS_DESCRIPTIONS)
    console.print(panels, markup=True, highlight=False)

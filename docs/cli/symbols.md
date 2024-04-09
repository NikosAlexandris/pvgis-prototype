---
icon: material/symbol
title: Symbols
tags:
  - Reference
  - Symbols
---

```python exec="true" html="true"
from pvgisprototype.constants import SYMBOL_DESCRIPTIONS
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE_HEAD
import os

table = Table(
    title='Symbols',
    caption='Symbols used throughout PVGIS\' command line interface',
    show_header=True,
    header_style="bold magenta",
    row_styles=['none', 'dim'],
    box=SIMPLE_HEAD,
    highlight=True,
)
table.add_column("Symbol", justify="right", style="bright_blue", no_wrap=True)
table.add_column("Description", style="cyan")
for symbol, description in SYMBOL_DESCRIPTIONS.items():
        table.add_row(f'[bold]{symbol}[/bold]', f'{description}')

with open(os.devnull, "w") as devnull:
    console = Console(record=True, width=150, file=devnull)
    console.print(table, markup=True, highlight=False)
print(console.export_html(inline_styles=True, code_format="<pre><code>{code}</code></pre>"))
```

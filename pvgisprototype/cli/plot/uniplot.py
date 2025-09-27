#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
This module contains code adapted from spiel by Josh Karpel
Original source: https://github.com/JoshKarpel/spiel/blob/bd64b7f2f04bdbe15c081360990ec6d4c93f0141/spiel/plot.py
License: MIT (https://github.com/JoshKarpel/spiel/blob/main/LICENSE)
"""

import re
from typing import Any, Iterable, Optional, Sequence, Union

import numpy as np
import uniplot
from colorama import Fore
from colorama import Style as CStyle
from rich.console import Console, ConsoleOptions
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

Plottable = Union[
    np.ndarray,
    Sequence[np.ndarray],
]

RE_ANSI_ESCAPE = re.compile(r"(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))")

COLOR_MAP = {
    Fore.RED: "red",
    Fore.GREEN: "green",
    Fore.BLUE: "blue",
    Fore.CYAN: "cyan",
    Fore.YELLOW: "yellow",
    Fore.MAGENTA: "magenta",
    Fore.BLACK: "black",
    Fore.WHITE: "white",
}


class Plot:
    def __init__(
        self,
        xs: Optional[Plottable] = None,
        ys: Optional[Plottable] = None,
        **options: Any,
    ) -> None:
        self.xs = xs
        self.ys = ys if ys is not None else []
        self.options = options

    def _ansi_to_text(self, s: str) -> Text:
        pieces = []
        tmp = ""
        style = Style.null()
        for char in RE_ANSI_ESCAPE.split(s):
            if char == CStyle.RESET_ALL:
                pieces.append(Text(tmp, style=style))
                style = Style.null()
                tmp = ""
            elif char in COLOR_MAP:
                pieces.append(Text(tmp, style=style))
                style = Style(color=COLOR_MAP[char])
                tmp = ""
            else:
                tmp += char

        # catch leftovers
        pieces.append(Text(tmp, style=style))

        return Text("", no_wrap=True).join(pieces)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> Iterable[Segment]:
        if self.options.get("height") is None and options.height is None:
            height = None
        else:
            height = max(
                (options.height - 5) if options.height else 1, self.options.get("height", 1)
            )

        plot_options = {
            **self.options,
            **dict(
                height=height,
                width=max(options.max_width - 10, self.options.get("width", 1)),
            ),
        }

        plot = "\n".join(uniplot.plot_to_string(xs=self.xs, ys=self.ys, **plot_options))


        text = self._ansi_to_text(plot)

        yield from text.__rich_console__(console, options)

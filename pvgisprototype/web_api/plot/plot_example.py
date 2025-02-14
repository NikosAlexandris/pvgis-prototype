from fastapi import Request


async def plot_example(request: Request, inline: bool = True):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = plot_line()

    return templates.TemplateResponse(
        "plot.html",
        {
            "request": request,
            "plot_script": script,
            "plot_div": div,
            "js_resources": js_resources,
            "css_resources": css_resources,
        },
    )


async def graph_example(request: Request, inline: bool = True):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    p = figure(title="Title for the plot", x_axis_type="datetime", y_axis_type="linear")

    script, div = components(p, INLINE)
    # script, div = plot_line()

    if inline:
        return template.render(
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
        )
    else:
        return templates.TemplateResponse(
            "graph.html",
            {
                "request": request,
                "plot_script": script,
                "plot_div": div,
                "js_resources": js_resources,
                "css_resources": css_resources,
            },
        )

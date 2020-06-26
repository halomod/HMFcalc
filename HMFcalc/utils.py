"""
Created on Jun 15, 2012

@author: Steven
"""
import copy
import io
import logging

import matplotlib.ticker as tick
from hmf import MassFunction
from hmf.wdm import MassFunctionWDM
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def hmf_driver(cls=MassFunction, previous=None, **kwargs):
    if previous is None:
        return cls(**kwargs)
    elif "wdm_model" in kwargs and not isinstance(previous, MassFunctionWDM):
        return MassFunctionWDM(**kwargs)
    elif "wdm_model" not in kwargs and isinstance(previous, MassFunctionWDM):
        return MassFunction(**kwargs)
    else:
        this = copy.deepcopy(previous)

        # TODO: this is a hack, and should be fixed in hmf
        # we have to set all _params whose model has been changed to {}
        # so that they don't get carry-over parameters from other models.
        for k, v in kwargs.items():
            if k.endswith("model") and v != getattr(this, k).__class__.__name__:
                this.update(**{k.replace("model", "params"): {}})

        this.update(**kwargs)

    return this


def create_canvas(objects, q, d, plot_format="png"):
    # TODO: make log scaling automatic
    fig = Figure(figsize=(10, 6), edgecolor="white", facecolor="white", dpi=100)
    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_xlabel(d["xlab"], fontsize=15)
    ax.set_ylabel(d["ylab"], fontsize=15)

    lines = ["-", "--", "-.", ":"]

    if q.startswith("comparison"):
        compare = True
        q = q[11:]
    else:
        compare = False

    if len(list(objects.values())[0].m) == len(getattr(list(objects.values())[0], q)):
        x = "m"
    else:
        x = "k"

    if not compare:
        for i, (l, o) in enumerate(objects.items()):
            y = getattr(o, q)
            ax.plot(
                getattr(o, x),
                y,
                color="C{}".format((i % 7)),
                linestyle=lines[(i // 7) % 4],
                label=l,
            )
    else:
        for i, (l, o) in enumerate(objects.items()):
            if i == 0:
                comp_obj = o
                continue

            y = getattr(o, q) / getattr(comp_obj, q)
            ax.plot(
                getattr(o, x),
                y,
                color="C{}".format((i + 1) % 7),
                linestyle=lines[((i + 1) // 7) % 4],
                label=l,
            )

    # Shrink current axis by 30%
    ax.set_xscale("log")

    ax.set_yscale(d["yscale"], basey=d.get("basey", 10))
    if d["yscale"] == "log":
        if d.get("basey", 10) == 2:
            ax.yaxis.set_major_formatter(tick.ScalarFormatter())

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=15)

    buf = io.BytesIO()

    if plot_format == "png":
        FigureCanvasAgg(fig).print_png(buf)
    elif plot_format == "pdf":
        FigureCanvasPdf(fig).print_pdf(buf)
    elif plot_format == "svg":
        FigureCanvasSVG(fig).print_svg(buf)
    else:
        raise ValueError("plot_format should be png, pdf or svg!")

    return buf

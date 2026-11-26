#!/usr/bin/env python3
"""results/ -> presentation/CUDA_Softmax_Kernel_Fusion.pptx  (same look as the GPU Retrieval Pipeline deck)"""
import os, sys, glob; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

df = load(); g = gpuinfo(); S = stats(df); O = observations(df, S); GPU = g.get("GPU", "GPU")
C = lambda h: RGBColor.from_string(h)
DARK, CARDD, TEAL, BLUE, PURP, RED, AMB, MUTE, CARDL = "0F1722", "182638", "35D0BA", "7AA2F7", "C3A6FF", "F07178", "F2B544", "8696AB", "E7ECF2"
P = Presentation(); P.slide_width = Inches(13.333); P.slide_height = Inches(7.5); BLANK = P.slide_layouts[6]
TITLE = "CUDA Softmax and Kernel Fusion"; LAB2 = "Parallel & Distributed Computing Laboratory"; N = [0]

def new(dark):
    s = P.slides.add_slide(BLANK); s.background.fill.solid(); s.background.fill.fore_color.rgb = C(DARK if dark else "FFFFFF"); N[0] += 1; s._dark = dark; return s
def tx(s, x, y, w, h, t, size=16, color=None, bold=False, font="Calibri", align=None, anchor=None, spacing=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    if anchor: tf.vertical_anchor = anchor
    lines = t if isinstance(t, list) else [t]
    for i, l in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); r = p.add_run(); r.text = l; f = r.font; f.size = Pt(size); f.bold = bold; f.name = font
        f.color.rgb = C(color or ("FFFFFF" if s._dark else "0F1722"));
        if align: p.alignment = align
        if spacing: p.space_after = Pt(spacing)
    return tb
def head(s, eyebrow, title):
    tx(s, .7, .45, 11.9, .3, eyebrow.upper(), 12, TEAL, True); tx(s, .7, .85, 11.9, .95, title, 32, bold=True)
    tx(s, .7, 7.05, 8, .3, f"{TITLE}  ·  {LAB2}", 9, MUTE); tx(s, 11.9, 7.05, .8, .3, str(N[0]), 9, MUTE, align=PP_ALIGN.RIGHT)
def lead(s, t, y=1.85, size=18, h=.9): tx(s, .7, y, 11.93, h, t, size)
def box(s, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); b.fill.solid(); b.fill.fore_color.rgb = C(fill)
    if line: b.line.color.rgb = C(line); b.line.width = Pt(1.25)
    else: b.line.fill.background()
    try: b.adjustments[0] = .06
    except Exception: pass
    b.shadow.inherit = False; return b
def card(s, x, y, w, h, title, body):
    box(s, x, y, w, h, CARDD if s._dark else CARDL); tx(s, x + .2, y + .15, w - .4, .4, title, 16, bold=True); tx(s, x + .2, y + .65, w - .4, h - .8, body, 13, MUTE if s._dark else "3B4656")
def stat(s, x, y, w, h, big, cap, color=TEAL):
    box(s, x, y, w, h, CARDD if s._dark else CARDL); tx(s, x + .25, y + .2, w - .5, .7, big, 30, color, True); tx(s, x + .25, y + 1.0, w - .5, h - 1.1, cap, 13, MUTE if s._dark else "3B4656")
def stages(s, items, hi=(), y=2.05, h=1.55):
    n = len(items); gap = .35; w = (11.93 - gap * (n - 1)) / n
    for i, (t, b) in enumerate(items):
        x = .7 + i * (w + gap); box(s, x, y, w, h, CARDD, AMB if i in hi else TEAL); tx(s, x + .12, y + .12, w - .24, .35, t, 14, bold=True, color="FFFFFF"); tx(s, x + .12, y + .55, w - .24, h - .6, b, 11, MUTE)
        if i < n - 1:
            a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + w + .04), Inches(y + h / 2 - .14), Inches(gap - .08), Inches(.28)); a.fill.solid(); a.fill.fore_color.rgb = C(AMB); a.line.fill.background()
def code(s, x, y, w, h, lines):
    box(s, x, y, w, h, CARDD); tx(s, x + .25, y + .2, w - .5, h - .3, lines, 13, "DDE6F0", font="Courier New")
def table(s, x, y, w, rows, headr, colw=None, size=12, rh=.37):
    t = s.shapes.add_table(len(rows) + 1, len(headr), Inches(x), Inches(y), Inches(w), Inches(rh * (len(rows) + 1))).table
    if colw:
        for j, cw in enumerate(colw): t.columns[j].width = Inches(w * cw / sum(colw))
    for j, h_ in enumerate(headr):
        c = t.cell(0, j); c.text = str(h_); c.fill.solid(); c.fill.fore_color.rgb = C(CARDD)
        p = c.text_frame.paragraphs[0]; p.runs[0].font.size = Pt(size); p.runs[0].font.bold = True; p.runs[0].font.color.rgb = C("FFFFFF")
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j); c.text = str(v); c.fill.solid(); c.fill.fore_color.rgb = C("FFFFFF" if i % 2 == 0 else CARDL)
            p = c.text_frame.paragraphs[0]; p.runs[0].font.size = Pt(size); p.runs[0].font.color.rgb = C("0F1722")
    return t
def chart(s, kind, cats, ser, x, y, w, h, colors, stacked=False, ytitle=None, numfmt='0.0'):
    cd = CategoryChartData(); cd.categories = [str(c) for c in cats]
    for k, v in ser.items(): cd.add_series(k, [None if (x_ is None or x_ != x_) else float(x_) for x_ in v])
    ct = {"line": XL_CHART_TYPE.LINE_MARKERS, "bar": XL_CHART_TYPE.COLUMN_STACKED if stacked else XL_CHART_TYPE.COLUMN_CLUSTERED, "hbar": XL_CHART_TYPE.BAR_STACKED}[kind]
    gf = s.shapes.add_chart(ct, Inches(x), Inches(y), Inches(w), Inches(h), cd); ch = gf.chart; fc = C("FFFFFF" if s._dark else "0F1722")
    ch.font.size = Pt(11); ch.font.color.rgb = fc; ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.color.rgb = fc
    ch.value_axis.has_major_gridlines = True; ch.value_axis.major_gridlines.format.line.color.rgb = C("2A3A52" if s._dark else "D5DBE5")
    ch.value_axis.tick_labels.font.color.rgb = fc; ch.category_axis.tick_labels.font.color.rgb = fc; ch.value_axis.tick_labels.number_format = numfmt; ch.value_axis.tick_labels.number_format_is_linked = False
    if ytitle: ch.value_axis.has_title = True; ch.value_axis.axis_title.text_frame.text = ytitle; ch.value_axis.axis_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11); ch.value_axis.axis_title.text_frame.paragraphs[0].runs[0].font.color.rgb = fc
    for sr, col in zip(ch.plots[0].series, colors):
        if kind == "line": sr.format.line.color.rgb = C(col); sr.format.line.width = Pt(2.25); sr.marker.format.fill.solid(); sr.marker.format.fill.fore_color.rgb = C(col); sr.marker.format.line.color.rgb = C(col); sr.smooth = False
        else: sr.format.fill.solid(); sr.format.fill.fore_color.rgb = C(col)
    return ch
def pic(s, name, x, y, w, h):
    from PIL import Image
    fn = os.path.join(RES, name)
    if not os.path.exists(fn): return
    iw, ih = Image.open(fn).size; sc = min(w / iw, h / ih); s.shapes.add_picture(fn, Inches(x), Inches(y), Inches(iw * sc), Inches(ih * sc))
def have(ex, var=None): d = df[df.exp == ex]; return len(d if var is None else d[d.variant == var]) > 0

cols = S["cols"]; sz = S["base_sizes"]; sp = dict(zip(sz, S["base_speed"]))
def bullets(s, x, y, w, h, items, size=15, color=None, gap=7):
    tx(s, x, y, w, h, ["•  " + i for i in items], size, color or ("D5DEE9" if s._dark else "26303D"), spacing=gap)
def cardb(s, x, y, w, h, title, body, size=16, sp=6):
    box(s, x, y, w, h, CARDD); tx(s, x + .25, y + .15, w - .5, .45, title, 18, "FFFFFF", True); tx(s, x + .25, y + .7, w - .5, h - .8, body, size, "C9D3E0", spacing=sp)
def label(s, x, y, w, t, color=TEAL, size=12): tx(s, x, y, w, .3, t.upper(), size, color, True)
def flow(s, items, y, h, hi=()):
    n = len(items); gap = .38; w = (11.93 - gap * (n - 1)) / n
    for i, (t, b) in enumerate(items):
        x = .7 + i * (w + gap); box(s, x, y, w, h, CARDD, AMB if i in hi else TEAL)
        tx(s, x + .12, y + .12, w - .24, .4, t, 15, "FFFFFF", True); tx(s, x + .12, y + .62, w - .24, h - .7, b, 12.5, "AFBBCB")
        if i < n - 1:
            a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + w + .05), Inches(y + h / 2 - .15), Inches(gap - .1), Inches(.3)); a.fill.solid(); a.fill.fore_color.rgb = C(AMB); a.line.fill.background()
def arrow(s, x, y, w=.32): 
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(.28)); a.fill.solid(); a.fill.fore_color.rgb = C(AMB); a.line.fill.background()

# 1 Title
s = new(True); tx(s, .9, 1.5, 11.5, .4, "PARALLEL AND DISTRIBUTED COMPUTING", 15, TEAL, True)
tx(s, .9, 2.1, 11.5, 1.8, "Softmax and Kernel Fusion using CUDA", 50, bold=True)
tx(s, .9, 4.3, 11.5, .5, "Team: Mudit Nayak  ·  Kartik  ·  Manoj  ·  Vinayak", 22)
tx(s, .9, 4.95, 11.5, .5, "KLE Technological University, Hubballi", 20, TEAL)

# 2 Intro
s = new(True); head(s, "Introduction and problem statement", "What is Softmax, and what is the problem?")
cardb(s, .7, 1.75, 5.85, 2.0, "What is Softmax?", ["•  Turns a list of scores into probabilities", "•  Every value is positive and they add up to 1", "•  Bigger score → bigger probability"], 15, 3)
cardb(s, 6.78, 1.75, 5.85, 2.0, "Why is it used in Machine Learning?", ["•  Classifiers: scores → class probabilities", "•  Transformers: attention uses a softmax on every row", "•  It runs again and again, so speed matters"], 15, 3)
box(s, .7, 3.95, 5.85, 2.85, CARDD); label(s, .95, 4.05, 5, "Example: scores to probabilities")
for i, (a_, b_) in enumerate([("2", "0.67"), ("1", "0.24"), ("0", "0.09")]):
    x = 1.0 + i * 1.75; box(s, x, 4.5, 1.3, .6, "24364F", BLUE); tx(s, x, 4.55, 1.3, .5, a_, 20, "FFFFFF", True, align=PP_ALIGN.CENTER)
    box(s, x, 5.7, 1.3, .6, "1E4A47", TEAL); tx(s, x, 5.75, 1.3, .5, b_, 20, "FFFFFF", True, align=PP_ALIGN.CENTER)
    a = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(x + .5), Inches(5.17), Inches(.3), Inches(.45)); a.fill.solid(); a.fill.fore_color.rgb = C(AMB); a.line.fill.background()
tx(s, 6.0 - .2, 5.0, 0.7, .8, "", 10)
box(s, 6.78, 3.95, 5.85, 1.5, CARDD, RED); label(s, 7.0, 4.03, 5.4, "Problem", RED)
tx(s, 7.0, 4.38, 5.45, 1.05, ["•  The usual version uses 3 separate GPU kernels", "•  Each one reads the same data again from slow global memory"], 14, "D5DEE9", spacing=4)
box(s, 6.78, 5.65, 5.85, 1.15, CARDD, TEAL); label(s, 7.0, 5.73, 5.4, "Objective")
tx(s, 7.0, 6.05, 5.45, .75, "Make softmax faster with CUDA by reducing memory trips, and check the answer against the CPU.", 14, "D5DEE9")

# 3 Architecture
s = new(True); head(s, "Project architecture and working", "How the project works")
flow(s, [("Input matrix", "Random float32 values, rows × columns"), ("Host code", "C++ / CUDA code on the CPU: copies data, launches kernels"), ("GPU kernels", "Softmax runs on many rows at once"), ("Output", "Probabilities for every row"), ("Benchmarking", "CUDA-event timing, CPU check, results to CSV")], 1.8, 1.75, hi=(2,))
for i, (t_, b_) in enumerate([("CPU", "Prepares the data, launches the kernels and computes the reference softmax to check against."), ("GPU", "Thousands of threads work in parallel. One block of threads handles one row."), ("CUDA", "The programming layer (CUDA C++ and nvcc) that lets our code run kernels on the GPU.")]):
    cardb(s, .7 + i * 4.1, 4.0, 3.75, 1.95, t_, b_, 15)
tx(s, .7, 6.15, 11.9, .6, "Python then reads the results file to draw the graphs.", 14, "AFBBCB")

# 4 Implementation + fusion
s = new(True); head(s, "Softmax implementation and kernel fusion", "Three steps, and how fusion saves memory trips")
for i, (t_, b_) in enumerate([("1  Find the maximum", "of the row"), ("2  Exponentials and sum", "exp(x − max), then add them up"), ("3  Normalise", "divide each value by the sum")]):
    x = .7 + i * 4.1; box(s, x, 1.65, 3.75, .95, CARDD, TEAL); tx(s, x + .15, 1.7, 3.5, .4, t_, 15, "FFFFFF", True); tx(s, x + .15, 2.15, 3.5, .4, b_, 12.5, "AFBBCB")
label(s, .7, 2.8, 4, "Separate: 3 kernels", RED)
for i, (k, d) in enumerate([("k_max", "reads the row"), ("k_sumexp", "reads the row again"), ("k_norm", "reads the row again, writes result")]):
    x = .7 + i * 2.55; box(s, x, 3.15, 2.2, 1.0, CARDD, RED); tx(s, x + .1, 3.2, 2.0, .35, k, 14, "FFFFFF", True, font="Courier New"); tx(s, x + .1, 3.6, 2.0, .5, d, 11.5, "AFBBCB")
    if i < 2: arrow(s, x + 2.22, 3.53, .3)
tx(s, 8.5, 3.2, 4.1, .9, ["4 global memory accesses", "per element"], 18, RED, True)
label(s, .7, 4.45, 4, "Fused: 1 kernel")
box(s, .7, 4.8, 7.5, 1.0, CARDD, TEAL); tx(s, .85, 4.85, 7.2, .35, "k_fused", 14, "FFFFFF", True, font="Courier New")
tx(s, .85, 5.25, 7.2, .5, "load row once into shared memory → max → sum → normalise → write once", 12.5, "AFBBCB")
tx(s, 8.5, 4.85, 4.1, .9, ["2 global memory accesses", "per element"], 18, TEAL, True)
tx(s, .7, 6.05, 11.9, .8, "Shared memory is a small, fast memory inside each block. The row is loaded once and reused for all three steps, so slow global memory is used half as often.", 14, "D5DEE9")

# 5 Techniques
s = new(True); head(s, "GPU optimisation techniques", "Four ways we made softmax faster")
T = [("Fused softmax (shared memory)", ["One block per row.", "The row is kept in shared memory,", "so global memory is read once and written once."], TEAL),
     ("Online softmax", ["Keeps a running maximum and running sum", "in a single pass; fixes the sum when a new", "maximum appears."], AMB),
     ("Warp-per-row", ["One warp (32 threads) handles a whole row.", "Values stay in registers, no shared memory.", "Used for rows up to 1024 columns."], BLUE),
     ("Fast math (__expf)", ["Uses the GPU's quicker, less exact exponential.", "In our tests it gave no consistent speedup", "(median 0.98×)."], PURP)]
for i, (t_, b_, col) in enumerate(T):
    x = .7 + (i % 2) * 6.1; y = 1.8 + (i // 2) * 2.5; box(s, x, y, 5.85, 2.2, CARDD, col); tx(s, x + .25, y + .18, 5.4, .45, t_, 18, col, True); tx(s, x + .25, y + .8, 5.4, 1.3, b_, 14.5, "D5DEE9", spacing=3)

# 6 Technologies
s = new(True); head(s, "Technologies and experimental setup", "What we used and how we tested")
cardb(s, .7, 1.75, 5.85, 4.5, "Technologies", ["•  C++ and CUDA C++ (nvcc)", "•  NVIDIA RTX 5060 Ti GPU", "•  Python, NumPy, Pandas and Matplotlib", "•  Ubuntu on WSL2"], 19, 12)
cardb(s, 6.78, 1.75, 5.85, 4.5, "Testing method", ["•  Different matrix sizes, row lengths (128 to 8192) and CUDA block sizes (64 to 1024)", "•  Timing with CUDA events: 3 warm-up runs, then the average of 30 runs", "•  CPU softmax (double precision) as the reference to check correctness"], 19, 12)

# 7 Results table
s = new(True); head(s, "Performance results", "Separate vs fused kernels")
show = [(4096, 1024), (4096, 2048), (4096, 4096), (8192, 2048)]
rows = [[f"{r} × {c}", f"{ms(df,'baseline','separate',r,c):.3f} ms", f"{ms(df,'baseline','fused_smem',r,c):.3f} ms", f"{sp[(r,c)]:.2f}×"] for r, c in show]
table(s, .7, 1.85, 7.7, rows, ["Matrix", "Separate", "Fused", "Speedup"], [1.6, 1.5, 1.5, 1.2], 17, .75)
box(s, 8.8, 1.85, 3.83, 3.75, CARDD, TEAL); tx(s, 9.0, 2.2, 3.4, 1.2, f"{max(sp.values()):.2f}×", 64, TEAL, True, align=PP_ALIGN.CENTER)
tx(s, 9.0, 3.65, 3.45, 1.7, "best speedup of the fused kernel over three separate kernels", 17, "D5DEE9", align=PP_ALIGN.CENTER)
lo = ms(df, "baseline", "separate", 2048, 8192) / ms(df, "baseline", "fused_smem", 2048, 8192)
tx(s, .7, 5.9, 11.9, .9, [f"Time per softmax call, {GPU}, float32 data. Very long rows gain less: 2048 × 8192 gave {lo:.2f}×."], 14, "AFBBCB")

# 8 Graphs
s = new(True); head(s, "Graphical performance analysis", "Fused is faster, and the best version depends on row length")
chart(s, "bar", [f"{r}×{c}" for r, c in show], {"3 separate kernels": [ms(df, "baseline", "separate", r, c) for r, c in show], "Fused kernel": [ms(df, "baseline", "fused_smem", r, c) for r, c in show]}, .7, 1.7, 5.7, 3.9, ["8696AB", TEAL], False, "time (ms)", '0.00')
ser = {}; cc = []
for v in ["fused_smem", "online", "warp_row"]:
    d = series(df, "colsweep", v, R=4096); se = series(df, "colsweep", "separate", R=4096)
    ser[LAB[v]] = [se[c] / d[c] if c in d.index else None for c in cols]; cc.append(COL[v].lstrip("#"))
chart(s, "line", cols, ser, 6.7, 1.7, 5.95, 3.9, cc, False, "speedup over separate (×)", '0.0')
tx(s, .7, 5.65, 5.7, .35, "Separate vs fused time (ms)", 12.5, "AFBBCB", align=PP_ALIGN.CENTER); tx(s, 6.7, 5.65, 5.95, .35, "Speedup across row lengths (columns, 4096 rows)", 12.5, "AFBBCB", align=PP_ALIGN.CENTER)
bullets(s, .7, 6.05, 11.9, .9, ["Short rows (up to 1024 columns): warp-per-row is fastest.   Long rows (8192): online softmax is fastest.   In between, fused and online are close."], 14, "D5DEE9")

# 9 Correctness, findings, limitations
s = new(True); head(s, "Correctness, findings and limitations", "Results are correct, and the lessons are clear")
box(s, .7, 1.75, 3.85, 4.95, CARDD, TEAL); label(s, .95, 1.88, 3.4, "Correctness")
tx(s, .95, 2.3, 3.4, .9, f"{S['n_checked']}", 48, TEAL, True); tx(s, .95, 3.25, 3.4, .5, "verified kernel runs", 15, "D5DEE9")
bullets(s, .95, 3.85, 3.45, 2.8, [f"Max absolute error: {S['maxerr']:.1e}", "All passed the 1 × 10⁻⁵ threshold"], 18, gap=10)
box(s, 4.75, 1.75, 3.85, 4.95, CARDD, AMB); label(s, 5.0, 1.88, 3.4, "Key findings", AMB)
bullets(s, 5.0, 2.35, 3.45, 4.2, ["Fusion reduces memory traffic", f"Fused softmax gives up to {max(sp.values()):.2f}× speedup on baseline sizes", "The best version depends on the workload size and row length"], 18, gap=14)
box(s, 8.8, 1.75, 3.83, 4.95, CARDD, RED); label(s, 9.05, 1.88, 3.4, "Limitations", RED)
bullets(s, 9.05, 2.35, 3.45, 4.2, ["Tested on one GPU", "Synthetic input data", "Shared-memory fused kernel needs the row to fit in shared memory (up to 12,288 columns)"], 18, gap=14)

# 10 Conclusion
s = new(True); head(s, "Conclusion", "What we achieved")
bullets(s, .7, 1.9, 7.2, 3.6, ["We built softmax on the GPU as 3 separate kernels, a fused kernel, online softmax, warp-per-row and fast-math versions", f"Fusing the kernels is up to {max(sp.values()):.2f}× faster on the baseline sizes", f"All {S['n_checked']} verified runs matched the CPU (max error {S['maxerr']:.1e})", "Fewer memory trips means a faster layer"], 18, gap=14)
box(s, 8.4, 1.9, 4.23, 3.4, CARDD, TEAL); tx(s, 8.6, 2.2, 3.85, 1.2, f"{max(sp.values()):.2f}×", 64, TEAL, True, align=PP_ALIGN.CENTER); tx(s, 8.6, 3.7, 3.85, 1.3, "faster with kernel fusion", 18, "D5DEE9", align=PP_ALIGN.CENTER)
tx(s, .7, 5.7, 11.9, .8, "Thank You", 40, TEAL, True); tx(s, .7, 6.4, 11.9, .5, "Mudit Nayak  ·  Kartik  ·  Manoj  ·  Vinayak", 18)

assert len(P.slides) == 10, len(P.slides)
out = os.path.join(ROOT, "presentation", "CUDA_Softmax_Kernel_Fusion_10slides.pptx"); P.save(out); print("written", out, len(P.slides), "slides")

#!/usr/bin/env python3
"""results/ -> X  (same look as the GPU Retrieval Pipeline deck)"""
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

sz = S["base_sizes"]; sp = S["base_speed"]; fw = lambda r, c: ms(df, "baseline", "fused_smem", r, c)
# ---- title
s = new(True); tx(s, .9, 1.2, 11.5, .4, "CUDA LAB EVALUATION  ·  THEME 10", 14, TEAL, True); tx(s, .9, 1.8, 11.5, 1.2, "Softmax and Kernel Fusion", 54, bold=True)
tx(s, .9, 3.0, 11.5, .7, "separate kernels versus one fused kernel, measured on a real GPU", 24, TEAL)
tx(s, .9, 4.2, 11.5, .5, "Name: Mudit Nayak     Roll No.: [add]     Theme No.: 10     Date: [add]", 20)
tx(s, .9, 4.8, 11.5, .5, "Team: Mudit · Kartik · Manoj · Vinayak     Guide: [add]", 18)
tx(s, .9, 5.4, 11.5, .4, f"KLE Technological University, Hubballi  ·  Parallel & Distributed Computing Lab  ·  {GPU}", 15, MUTE)

# ---- CP1
s = new(False); head(s, "Checkpoint 1", "Softmax concept")
box(s, .7, 1.7, 11.93, 1.25, CARDL)
tx(s, .9, 1.78, 11.5, .45, "softmax(x)ᵢ  =  exp(xᵢ − m) / Σⱼ exp(xⱼ − m),     m = max over the row", 24, bold=True, font="Cambria")
tx(s, .9, 2.35, 11.5, .5, "Turns any row of scores into probabilities that are positive and sum to 1. Applied independently to every row.", 14, "3B4656")
card(s, .7, 3.2, 3.85, 3.55, "Why subtract the row max", ["exp(x) overflows float32 for x > ~88, giving inf and then NaN.", "", "Example row [1000, 999]: exp(1000)/(exp(1000)+exp(999)) is inf/inf = NaN.", "Shifted by m = 1000: [0, −1] → [1, 0.368] / 1.368 = [0.731, 0.269].", "", "Same answer, no overflow."])
card(s, 4.75, 3.2, 3.85, 3.55, "Where it appears", ["Classifiers: the last layer turns class scores into probabilities.", "", "Attention: one softmax per row of the QKᵀ score matrix, in every head of every transformer layer.", "", "So it runs enormously often."])
card(s, 8.8, 3.2, 3.83, 3.55, "What the GPU must do per row", ["1. Reduce the row to its max.", "2. Reduce exp(x − m) to a sum.", "3. Divide each exp(x − m) by the sum.", "", "Two reductions plus one element-wise pass, with almost no arithmetic per byte: a memory-bound layer."])

# ---- CP2
s = new(True); head(s, "Checkpoint 2", "Separate kernels")
for i, (t_, b_) in enumerate([("k_max", "row maximum"), ("k_sumexp", "Σ exp(x − max)"), ("k_norm", "write exp(x − max) / sum")]):
    x = .7 + i * 4.1; box(s, x, 1.7, 3.7, 1.0, CARDD, TEAL); tx(s, x + .15, 1.75, 3.4, .4, t_ + "  <<<rows, 256>>>", 14, "FFFFFF", True, font="Courier New"); tx(s, x + .15, 2.2, 3.4, .4, b_, 13, MUTE)
rows = [[f"{r}×{c}", fmt(ms(df, "baseline", "sep_max", r, c)), fmt(ms(df, "baseline", "sep_sum", r, c)), fmt(ms(df, "baseline", "sep_norm", r, c)), fmt(ms(df, "baseline", "separate", r, c))] for r, c in sz]
table(s, .7, 3.0, 11.93, rows, ["Matrix (rows × cols)", "max (ms)", "sum of exp (ms)", "normalise (ms)", "all three, total (ms)"], [2.2, 1.5, 1.8, 1.8, 2.2], 13, .44)
tx(s, .7, 5.85, 11.93, 1.0, ["One block per row, 256 threads, 3 launches: each kernel re-reads the row from global memory (4 global accesses per element in all).", f"Times: CUDA events, 3 warm-up runs then the average of 30 runs, on the {GPU}. Component times are measured standalone, so they need not add exactly to the total."], 13, MUTE, spacing=4)

# ---- CP3
s = new(False); head(s, "Checkpoint 3", "Fused kernel")
for i, (t_, b_) in enumerate([("1  Load once", "Each thread loads a strided slice of the row into shared memory while tracking its local max."), ("2  Reduce twice", "Warp shuffles, then shared memory + __syncthreads, give the block the max, then the sum of exp(x − max). No global access."), ("3  Write once", "Normalise straight from shared memory and write y.")]):
    card(s, .7 + i * 4.1, 1.7, 3.75, 2.15, t_, b_)
code(s, .7, 4.1, 5.6, 1.15, ["k_fused<<<rows, 256, cols*4>>>(x, y, cols);", "extern __shared__ float row[];   // one row"])
box(s, 6.6, 4.1, 6.03, 2.7, CARDL)
tx(s, 6.8, 4.2, 5.7, .4, "Global memory traffic saved", 16, bold=True)
tx(s, 6.8, 4.7, 5.7, 2.0, ["Separate: read x (max) + read x (sum) + read x and write y (normalise) = 4 accesses per element.", "Fused: read x once, write y once = 2 accesses per element.", "Half the traffic, and 1 launch instead of 3. In bytes, 4096×4096: 268 MB → 134 MB."], 13, "3B4656", spacing=5)
tx(s, .7, 5.45, 5.6, 1.4, "Limit: the row must fit in shared memory (cols × 4 bytes ≤ 48 KB, so up to 12,288 columns).", 13, "3B4656")

# ---- CP4
s = new(True); head(s, "Checkpoint 4", "Results table")
rows = [[f"{r}×{c}", fmt(ms(df, "baseline", "separate", r, c)), fmt(ms(df, "baseline", "fused_smem", r, c)), f"{x:.2f}×", f"{4*r*c*4/1e6:.1f}", f"{2*r*c*4/1e6:.1f}", f"{df[(df.exp=='baseline')&(df.variant=='fused_smem')&(df.rows==r)&(df.cols==c)].err.iloc[0]:.1e}", "MATCH"] for (r, c), x in zip(sz, sp)]
table(s, .7, 1.75, 11.93, rows, ["Matrix", "Separate (ms)", "Fused (ms)", "Speedup", "Bytes moved, separate (MB)", "Bytes moved, fused (MB)", "Max error vs CPU", "Output"], [1.3, 1.3, 1.2, 1.1, 1.9, 1.8, 1.5, 1.0], 12, .5)
tx(s, .7, 5.15, 11.93, 1.8, [f"GPU: {GPU}   ·   float32 inputs, uniform random in [−10, 10]   ·   block = 256 threads", "Time = average of 30 runs after 3 warm-up runs (CUDA events). Bytes moved are estimates: ideal accesses × elements × 4 bytes, not hardware counters.", f"CPU check: double-precision softmax on the first 64 rows of every matrix; all {S['n_checked']} verified runs match (worst error {S['maxerr']:.1e}, threshold 1e-5)."], 14, MUTE, spacing=6)

# ---- CP5
s = new(False); head(s, "Checkpoint 5", "Analysis")
card(s, .7, 1.7, 3.85, 4.1, "Why fusion helps", ["Softmax does very little arithmetic per byte, so time is set by memory traffic.", "", f"Fusing cut ideal traffic from 4 accesses to 2 and gave {min(sp):.2f}–{max(sp):.2f}× on the baseline sizes (about 2× is the ceiling).", "", f"On 268 MB matrices the fused kernel reaches {float(S['dram_fused'].gbps.min()):.0f}–{float(S['dram_fused'].gbps.max()):.0f} GB/s, about {float(S['dram_fused'].gbps.max())/PEAK*100:.0f}% of the 448 GB/s spec peak. A faster __expf made no consistent difference."])
bb = S["best_block"]
card(s, 4.75, 1.7, 3.85, 4.1, "Row length and block size", ["Fused kernel, best block size by row length:", ""] + [f"{c} columns → {int(b)} threads" for c, b in sorted(bb.items())] + ["", "Short rows want small blocks (1024 threads is 3.9× slower at 1024 columns than 128); long rows want 512. At 8192 columns, 64 threads is 3.9× slower than 512.", "Long rows also lose the speedup (1.41× at 8192 columns)."])
card(s, 8.8, 1.7, 3.83, 4.1, "Industry use", ["Deep learning compilers and inference engines fuse small kernels like these to cut memory traffic and cost.", "", "Examples: TensorRT, PyTorch torch.compile / XLA fusing element-wise and reduction ops, and FlashAttention, which fuses the attention softmax so the score matrix is never written to global memory."])
tx(s, .7, 6.0, 11.93, .9, "Explanations of the block-size and long-row trends are our hypotheses (occupancy and shared-memory use); they have not been confirmed with a profiler such as Nsight Compute.", 12, "3B4656")

out = os.path.join(ROOT, "presentation", "CUDA_Softmax_Kernel_Fusion_5CP.pptx"); P.save(out); print("written", out, len(P.slides), "slides")

import random
import tkinter as tk
from tkinter import font as tkfont

PALETTE = {
    "bg_top": "#DCEEFF",
    "bg_bottom": "#F5E1F5",
    "card_fill": "#FFFFFF",
    "card_border": "#D8C7F5",
    "card_fill_alt": "#FFF3FA",
    "card_border_alt": "#F6D3E6",
    "text": "#5B5B7A",
    "text_soft": "#9A96B5",
    "accent": "#B39DDB",
    "accent_dark": "#9575CD",
    "accent_pink": "#FFAFC5",
    "accent_pink_dark": "#F48FB1",
    "status_on": "#4CAF93",
    "status_off": "#FF8FA3",
    "restart": "#FFC98E",
    "restart_dark": "#F5A855",
    "entry_bg": "#F6F3FC",
    "bubble_colors": ["#F7D9EA", "#D9E8FB", "#E5D9F7", "#FCE7F3"],
}

FONT_FAMILY = "Microsoft YaHei UI"


def font_normal(size=10):
    return (FONT_FAMILY, size)


def font_bold(size=11):
    return (FONT_FAMILY, size, "bold")


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def draw_vertical_gradient(canvas, width, height, color_top, color_bottom):
    canvas.delete("gradient")
    r1, g1, b1 = _hex_to_rgb(color_top)
    r2, g2, b2 = _hex_to_rgb(color_bottom)
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        canvas.create_line(0, y, width, y, fill=_rgb_to_hex((r, g, b)), tags="gradient")
    canvas.tag_lower("gradient")


def draw_bubbles(canvas, width, height, colors, seed=7):
    rng = random.Random(seed)
    for _ in range(6):
        r = rng.randint(30, 70)
        x = rng.randint(-20, width - 20)
        y = rng.randint(-20, height - 20)
        color = rng.choice(colors)
        canvas.create_oval(x, y, x + r, y + r, fill=color, outline="", tags="bubble")
    canvas.tag_lower("bubble")
    canvas.tag_raise("bubble", "gradient")


def rounded_rect(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def make_card(canvas, x, y, w, h, radius=18, fill="#FFFFFF", border="#D8C7F5", border_width=2):
    return rounded_rect(canvas, x, y, x + w, y + h, radius=radius, fill=fill, outline=border, width=border_width)


class RoundedButton(tk.Canvas):
    """圆角药丸按钮,纯 Canvas 画出来的,tkinter 原生控件做不到真正的圆角。"""

    def __init__(self, parent, text, command=None, radius=16,
                 bg="#B39DDB", hover_bg="#9575CD", fg="white",
                 font=None, padx=18, pady=8, **kwargs):
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg
        self.fg_color = fg
        self.radius = radius
        self.font = font or font_normal(10)

        f = tkfont.Font(font=self.font)
        text_w = f.measure(text)
        text_h = f.metrics("linespace")
        width = text_w + padx * 2
        height = text_h + pady * 2

        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, **kwargs)

        self._shape = rounded_rect(self, 1, 1, width - 1, height - 1, radius=radius, fill=bg, outline="")
        self._text = self.create_text(width / 2, height / 2, text=text, fill=fg, font=self.font)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _event):
        self.itemconfig(self._shape, fill=self.hover_color)
        self.configure(cursor="hand2")

    def _on_leave(self, _event):
        self.itemconfig(self._shape, fill=self.bg_color)

    def _on_click(self, _event):
        if self.command:
            self.command()

    def set_text(self, text):
        self.itemconfig(self._text, text=text)


class PillToggle(tk.Canvas):
    """iOS 风格的胶囊开关,点一下切换绑定的 BooleanVar。"""

    def __init__(self, parent, variable, on_color=None, off_color=None,
                 command=None, width=50, height=26, background=None, **kwargs):
        self.variable = variable
        self.on_color = on_color or PALETTE["status_on"]
        self.off_color = off_color or "#D9D3E8"
        self.command = command
        self._toggle_w = width
        self._toggle_h = height

        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0,
                          background=background or PALETTE["card_fill"], **kwargs)

        radius = height / 2
        self._track = rounded_rect(self, 1, 1, width - 1, height - 1, radius=radius, fill=self.off_color, outline="")
        pad = 3
        knob_d = height - 2 * pad
        self._knob = self.create_oval(pad, pad, pad + knob_d, pad + knob_d, fill="white", outline="")

        self.bind("<Button-1>", self._on_click)
        self.configure(cursor="hand2")
        self._render()

    def _on_click(self, _event):
        self.variable.set(not self.variable.get())
        self._render()
        if self.command:
            self.command()

    def _render(self):
        pad = 3
        knob_d = self._toggle_h - 2 * pad
        if self.variable.get():
            self.itemconfig(self._track, fill=self.on_color)
            self.coords(self._knob, self._toggle_w - pad - knob_d, pad, self._toggle_w - pad, pad + knob_d)
        else:
            self.itemconfig(self._track, fill=self.off_color)
            self.coords(self._knob, pad, pad, pad + knob_d, pad + knob_d)

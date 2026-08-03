import tkinter as tk

from ui_theme import PALETTE, RoundedButton, font_bold, font_normal


class StudyTimer(tk.Frame):
    """本地学习计时器,纯本地显示,不和任何 provider 打交道。"""

    def __init__(self, master, bg=None):
        self.bg_color = bg or PALETTE["card_fill_alt"]
        super().__init__(master, bg=self.bg_color)

        self.mode = tk.StringVar(value="stopwatch")
        self.minutes_var = tk.StringVar(value="25")
        self.remaining_seconds = 0
        self.running = False
        self._after_id = None

        mode_frame = tk.Frame(self, bg=self.bg_color)
        mode_frame.pack(fill="x", pady=(0, 6))

        common_radio_opts = dict(
            bg=self.bg_color,
            fg=PALETTE["text"],
            selectcolor=PALETTE["card_fill"],
            activebackground=self.bg_color,
            font=font_normal(10),
            highlightthickness=0,
        )

        tk.Radiobutton(
            mode_frame, text="⏱ 正计时", variable=self.mode, value="stopwatch",
            command=self._on_mode_change, **common_radio_opts,
        ).pack(side="left")
        tk.Radiobutton(
            mode_frame, text="⏳ 倒计时", variable=self.mode, value="countdown",
            command=self._on_mode_change, **common_radio_opts,
        ).pack(side="left", padx=(10, 0))

        tk.Label(mode_frame, text="分钟:", bg=self.bg_color, fg=PALETTE["text"],
                 font=font_normal(10)).pack(side="left", padx=(20, 4))
        self.minutes_entry = tk.Entry(
            mode_frame, textvariable=self.minutes_var, width=6,
            bg=PALETTE["entry_bg"], fg=PALETTE["text"], relief="flat",
            highlightthickness=1, highlightbackground=PALETTE["card_border_alt"],
            highlightcolor=PALETTE["accent_pink_dark"], font=font_normal(10),
        )
        self.minutes_entry.pack(side="left", ipady=2)

        self.display_label = tk.Label(
            self, text="00:00:00", font=(font_normal()[0], 30, "bold"),
            bg=self.bg_color, fg=PALETTE["accent_dark"],
        )
        self.display_label.pack(pady=8)

        button_frame = tk.Frame(self, bg=self.bg_color)
        button_frame.pack()

        self.start_button = RoundedButton(
            button_frame, "开始", command=self.start, bg=PALETTE["status_on"],
            hover_bg="#3D9B7E", font=font_bold(10), background=self.bg_color,
        )
        self.start_button.pack(side="left", padx=5)

        self.pause_button = RoundedButton(
            button_frame, "暂停", command=self.pause, bg=PALETTE["accent"],
            hover_bg=PALETTE["accent_dark"], font=font_bold(10), background=self.bg_color,
        )
        self.pause_button.pack(side="left", padx=5)

        self.reset_button = RoundedButton(
            button_frame, "重置", command=self.reset, bg=PALETTE["accent_pink"],
            hover_bg=PALETTE["accent_pink_dark"], font=font_bold(10), background=self.bg_color,
        )
        self.reset_button.pack(side="left", padx=5)

        self._on_mode_change()

    def _on_mode_change(self):
        is_countdown = self.mode.get() == "countdown"
        self.minutes_entry.configure(state="normal" if is_countdown else "disabled")
        if not self.running:
            self.reset()

    def _format(self, total_seconds):
        total_seconds = max(0, int(total_seconds))
        h, rem = divmod(total_seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _initial_seconds(self):
        if self.mode.get() == "countdown":
            try:
                minutes = float(self.minutes_var.get())
            except ValueError:
                minutes = 0
            return max(0, int(minutes * 60))
        return 0

    def start(self):
        if self.running:
            return
        if self.remaining_seconds == 0 and self.mode.get() == "countdown":
            self.remaining_seconds = self._initial_seconds()
        self.running = True
        self._tick()

    def pause(self):
        self.running = False
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def reset(self):
        self.pause()
        if self.mode.get() == "countdown":
            self.remaining_seconds = self._initial_seconds()
        else:
            self.remaining_seconds = 0
        self.display_label.configure(text=self._format(self.remaining_seconds))

    def _tick(self):
        if not self.running:
            return

        if self.mode.get() == "countdown":
            if self.remaining_seconds <= 0:
                self.running = False
                self.display_label.configure(text="00:00:00")
                return
            self.remaining_seconds -= 1
        else:
            self.remaining_seconds += 1

        self.display_label.configure(text=self._format(self.remaining_seconds))
        self._after_id = self.after(1000, self._tick)

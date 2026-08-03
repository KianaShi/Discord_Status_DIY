import json
import os
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox

from providers.discord_provider import DiscordProvider
from timer_widget import StudyTimer
from ui_theme import (
    PALETTE,
    PillToggle,
    RoundedButton,
    draw_bubbles,
    draw_vertical_gradient,
    font_bold,
    font_normal,
    make_card,
)

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "discord": {
        "enabled": True,
        "client_id": "",
        "details": "",
    },
}

WINDOW_W, WINDOW_H = 560, 560

CARD1 = (20, 20, 520, 260)   # Discord 设置卡片: x, y, w, h
CARD2 = (20, 300, 520, 240)  # 计时器卡片
CARD_RADIUS = 20


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return json.loads(json.dumps(DEFAULT_CONFIG))
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for section in merged:
        if section in data:
            merged[section].update(data[section])
    return merged


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("自定义状态展示工具 ✨")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.resizable(False, False)
        self.root.configure(bg=PALETTE["bg_top"])

        self.config_data = load_config()

        self.discord_provider = None

        self._build_background()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        threading.Thread(target=self._connect_providers, daemon=True).start()

    def _build_background(self):
        self.bg_canvas = tk.Canvas(self.root, width=WINDOW_W, height=WINDOW_H, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, width=WINDOW_W, height=WINDOW_H)
        draw_vertical_gradient(self.bg_canvas, WINDOW_W, WINDOW_H, PALETTE["bg_top"], PALETTE["bg_bottom"])
        draw_bubbles(self.bg_canvas, WINDOW_W, WINDOW_H, PALETTE["bubble_colors"])

        make_card(self.bg_canvas, *CARD1, radius=CARD_RADIUS,
                  fill=PALETTE["card_fill"], border=PALETTE["card_border"])
        make_card(self.bg_canvas, *CARD2, radius=CARD_RADIUS,
                  fill=PALETTE["card_fill_alt"], border=PALETTE["card_border_alt"])

    def _build_ui(self):
        x, y, w, h = CARD1
        inset = CARD_RADIUS
        discord_holder = tk.Frame(self.root, bg=PALETTE["card_fill"])
        discord_holder.place(x=x + inset, y=y + inset, width=w - 2 * inset, height=h - 2 * inset)
        discord_holder.lift()

        tk.Label(
            discord_holder, text="🎮 Discord 状态推送", bg=PALETTE["card_fill"],
            fg=PALETTE["accent_dark"], font=font_bold(13),
        ).pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(discord_holder, bg=PALETTE["card_fill"])
        form_frame.pack(fill="both", expand=True)
        self._build_discord_form(form_frame)

        x2, y2, w2, h2 = CARD2
        timer_holder = tk.Frame(self.root, bg=PALETTE["card_fill_alt"])
        timer_holder.place(x=x2 + inset, y=y2 + inset, width=w2 - 2 * inset, height=h2 - 2 * inset)
        timer_holder.lift()

        tk.Label(
            timer_holder, text="📚 学习计时器", bg=PALETTE["card_fill_alt"],
            fg=PALETTE["accent_pink_dark"], font=font_bold(13),
        ).pack(anchor="w", pady=(0, 6))

        StudyTimer(timer_holder, bg=PALETTE["card_fill_alt"]).pack(fill="both", expand=True)

    def _labeled_entry(self, parent, row, label_text, variable):
        tk.Label(parent, text=label_text, bg=PALETTE["card_fill"], fg=PALETTE["text"],
                 font=font_normal(10)).grid(row=row, column=0, sticky="w", pady=6, padx=(4, 8))
        entry = tk.Entry(
            parent, textvariable=variable, width=32,
            bg=PALETTE["entry_bg"], fg=PALETTE["text"], relief="flat",
            highlightthickness=1, highlightbackground=PALETTE["card_border"],
            highlightcolor=PALETTE["accent_dark"], font=font_normal(10),
        )
        entry.grid(row=row, column=1, pady=6, ipady=3)
        return entry

    def _build_enable_toggle(self, parent, row, variable, state_label_attr):
        toggle_frame = tk.Frame(parent, bg=PALETTE["card_fill"])
        toggle_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=4, pady=(0, 10))

        tk.Label(
            toggle_frame, text="启用状态推送:", bg=PALETTE["card_fill"],
            fg=PALETTE["text"], font=font_normal(10),
        ).pack(side="left", padx=(0, 8))

        state_label = tk.Label(toggle_frame, bg=PALETTE["card_fill"], font=font_bold(10))
        setattr(self, state_label_attr, state_label)

        def refresh(*_args):
            if variable.get():
                state_label.configure(text="已启用", fg=PALETTE["status_on"])
            else:
                state_label.configure(text="已停用", fg=PALETTE["text_soft"])

        PillToggle(
            toggle_frame, variable=variable, command=refresh, background=PALETTE["card_fill"],
        ).pack(side="left")
        state_label.pack(side="left", padx=(8, 0))

        refresh()

    def _build_discord_form(self, parent):
        cfg = self.config_data["discord"]
        for i in range(2):
            parent.grid_columnconfigure(i, pad=4)

        self.discord_client_id = tk.StringVar(value=cfg["client_id"])
        self._labeled_entry(parent, 0, "Client ID:", self.discord_client_id)

        self.discord_details = tk.StringVar(value=cfg["details"])
        self._labeled_entry(parent, 1, "显示文字:", self.discord_details)

        button_frame = tk.Frame(parent, bg=PALETTE["card_fill"])
        button_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=(10, 4))
        RoundedButton(
            button_frame, "打开Discord图标上传页面", command=self._open_discord_assets_page,
            bg=PALETTE["accent_pink"], hover_bg=PALETTE["accent_pink_dark"],
            font=font_normal(9), background=PALETTE["card_fill"],
        ).pack(side="left")
        RoundedButton(
            button_frame, "保存", command=self._save_discord,
            bg=PALETTE["accent"], hover_bg=PALETTE["accent_dark"],
            font=font_bold(10), background=PALETTE["card_fill"],
        ).pack(side="left", padx=10)
        RoundedButton(
            button_frame, "重启", command=self._restart_discord,
            bg=PALETTE["restart"], hover_bg=PALETTE["restart_dark"],
            font=font_bold(10), background=PALETTE["card_fill"],
        ).pack(side="left")

        self.discord_enabled = tk.BooleanVar(value=cfg.get("enabled", True))
        self._build_enable_toggle(parent, 3, self.discord_enabled, "discord_state_label")

        self.discord_status_var = tk.StringVar(
            value="○ 尚未连接" if self.discord_enabled.get() else "○ 已停用(未启用推送)"
        )
        self.discord_status_label = tk.Label(
            parent, textvariable=self.discord_status_var, bg=PALETTE["card_fill"],
            fg=PALETTE["status_off"] if self.discord_enabled.get() else PALETTE["text_soft"],
            font=font_normal(10),
        )
        self.discord_status_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=(10, 0))

    def _open_discord_assets_page(self):
        client_id = self.discord_client_id.get().strip()
        if not client_id:
            messagebox.showwarning("提示", "请先填写 Discord Client ID")
            return
        webbrowser.open(f"https://discord.com/developers/applications/{client_id}/rich-presence/assets")

    def _collect_discord_config(self):
        self.config_data["discord"].update(
            {
                "enabled": self.discord_enabled.get(),
                "client_id": self.discord_client_id.get().strip(),
                "details": self.discord_details.get().strip(),
            }
        )

    def _save_discord(self):
        self._collect_discord_config()
        self._write_config()
        messagebox.showinfo("已保存", "配置已保存,需要重启软件才能生效")

    def _restart_discord(self):
        self._collect_discord_config()
        self._write_config()
        self._restart_app()

    def _restart_app(self):
        if self.discord_provider is not None:
            self.discord_provider.clear_status()
            self.discord_provider.close()
        self.root.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _write_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)

    def _connect_providers(self):
        discord_cfg = self.config_data["discord"]
        if discord_cfg.get("enabled") and discord_cfg.get("client_id"):
            self._connect_discord(discord_cfg)

    def _set_status(self, label, var, text, ok):
        var.set(text)
        label.configure(fg=PALETTE["status_on"] if ok else PALETTE["status_off"])

    def _connect_discord(self, cfg):
        try:
            provider = DiscordProvider(cfg["client_id"], cfg["details"], "")
            provider.connect()
            provider.update_status(cfg["details"], "")
            self.discord_provider = provider
            self.root.after(
                0, lambda: self._set_status(self.discord_status_label, self.discord_status_var, "● 已连接", True)
            )
        except Exception as e:
            msg = str(e)
            self.root.after(
                0,
                lambda msg=msg: self._set_status(
                    self.discord_status_label, self.discord_status_var, f"○ 未连接: {msg}", False
                ),
            )

    def on_close(self):
        if self.discord_provider is not None:
            self.discord_provider.clear_status()
            self.discord_provider.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

import socket
import threading
import queue
from datetime import datetime
import os
import sys

import pyperclip
import customtkinter as ctk
from flask import Flask, request, jsonify

# -----------------------------
# Flask backend
# -----------------------------
app = Flask(__name__)
message_queue = queue.Queue()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


@app.route("/", methods=["GET"])
def home():
    return "TextBridge desktop server is running"


@app.route("/text", methods=["POST"])
def receive_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"ok": False, "error": "Empty text"}), 400

    pyperclip.copy(text)
    message_queue.put({
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    return jsonify({
        "ok": True,
        "message": "Copied to clipboard"
    })


def run_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


# -----------------------------
# Desktop App (CustomTkinter)
# -----------------------------
class MessageBubble(ctk.CTkFrame):
    def __init__(self, master, text, time_text, copy_callback, status_callback, is_latest=False, *args, **kwargs):
        self.is_latest = is_latest
        self.status_callback = status_callback

        self.normal_fg = "#162133"
        self.normal_border = "#26344b"
        self.normal_header = "#1c2940"

        self.pop_fg_1 = "#22324f"
        self.pop_border_1 = "#5a84da"
        self.pop_header_1 = "#2b3e60"

        self.pop_fg_2 = "#1c2a42"
        self.pop_border_2 = "#466cb8"
        self.pop_header_2 = "#243754"

        super().__init__(
            master,
            corner_radius=18,
            fg_color=self.pop_fg_1 if is_latest else self.normal_fg,
            border_width=1,
            border_color=self.pop_border_1 if is_latest else self.normal_border,
            *args,
            **kwargs
        )

        self.full_text = text
        self.copy_callback = copy_callback

        self.header = ctk.CTkFrame(
            self,
            fg_color=self.pop_header_1 if is_latest else self.normal_header,
            corner_radius=14
        )
        self.header.pack(fill="x", padx=10, pady=(10, 8))

        left_label = ctk.CTkLabel(
            self.header,
            text="Android",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#dbe7ff"
        )
        left_label.pack(side="left", padx=12, pady=8)

        right_label = ctk.CTkLabel(
            self.header,
            text=time_text,
            font=ctk.CTkFont(size=11),
            text_color="#9fb3d9"
        )
        right_label.pack(side="right", padx=12, pady=8)

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.textbox = ctk.CTkTextbox(
            self.body,
            wrap="word",
            fg_color="#162133",
            text_color="#f8fbff",
            border_width=0,
            corner_radius=0,
            activate_scrollbars=False,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=80
        )
        self.textbox.pack(fill="x", expand=True)
        self.textbox.insert("1.0", text)
        self.textbox.configure(state="disabled")

        self._fit_height()

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=14, pady=(0, 12))

        copy_btn = ctk.CTkButton(
            self.footer,
            text="Copy",
            width=82,
            height=34,
            corner_radius=12,
            fg_color="#243554",
            hover_color="#2e456d",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.copy_callback(self.full_text)
        )
        copy_btn.pack(side="left")

        self.textbox.bind("<Button-3>", self.show_context_menu)
        self.textbox.bind("<Control-c>", self.copy_selected)

        if self.is_latest:
            self.after(40, self.animate_bubble_pop)

    def ease_out_back(self, t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    def lerp(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def animate_bubble_pop(self):
        self.anim_step = 0
        self.anim_steps = 16

        self.start_padx = 78
        self.end_padx = 10

        self.start_header_padx = 18
        self.end_header_padx = 10

        self.start_body_padx = 20
        self.end_body_padx = 14

        self.start_footer_padx = 20
        self.end_footer_padx = 14

        self.start_fg = self.pop_fg_1
        self.start_border = self.pop_border_1
        self.start_header = self.pop_header_1

        self.end_fg = self.normal_fg
        self.end_border = self.normal_border
        self.end_header = self.normal_header

        self._animate_bubble_frame()

    def _animate_bubble_frame(self):
        t = self.anim_step / self.anim_steps
        e = self.ease_out_back(t)

        padx_now = int(self.lerp(self.start_padx, self.end_padx, e))
        header_padx_now = int(self.lerp(self.start_header_padx, self.end_header_padx, e))
        body_padx_now = int(self.lerp(self.start_body_padx, self.end_body_padx, e))
        footer_padx_now = int(self.lerp(self.start_footer_padx, self.end_footer_padx, e))

        try:
            self.pack_configure(padx=(0, padx_now))
            self.header.pack_configure(padx=header_padx_now, pady=(10, 8))
            self.body.pack_configure(padx=body_padx_now, pady=(0, 8))
            self.footer.pack_configure(padx=footer_padx_now, pady=(0, 12))
        except Exception:
            pass

        if t < 0.35:
            self.configure(fg_color=self.pop_fg_1, border_color=self.pop_border_1)
            self.header.configure(fg_color=self.pop_header_1)
        elif t < 0.7:
            self.configure(fg_color=self.pop_fg_2, border_color=self.pop_border_2)
            self.header.configure(fg_color=self.pop_header_2)
        else:
            self.configure(fg_color=self.normal_fg, border_color=self.normal_border)
            self.header.configure(fg_color=self.normal_header)

        if self.anim_step < self.anim_steps:
            self.anim_step += 1
            self.after(16, self._animate_bubble_frame)   # ~60 FPS
        else:
            self.configure(fg_color=self.normal_fg, border_color=self.normal_border)
            self.header.configure(fg_color=self.normal_header)
            try:
                self.pack_configure(padx=(0, self.end_padx))
                self.header.pack_configure(padx=self.end_header_padx, pady=(10, 8))
                self.body.pack_configure(padx=self.end_body_padx, pady=(0, 8))
                self.footer.pack_configure(padx=self.end_footer_padx, pady=(0, 12))
            except Exception:
                pass

    def _fit_height(self):
        self.textbox.configure(state="normal")
        line_count = int(self.textbox.index("end-1c").split(".")[0])
        pixels = max(74, min(420, 28 + line_count * 24))
        self.textbox.configure(height=pixels)
        self.textbox.configure(state="disabled")

    def copy_selected(self, event=None):
        try:
            selected = self.textbox.get("sel.first", "sel.last")
            pyperclip.copy(selected)
            self.status_callback("Selected text copied")
        except Exception:
            self.status_callback("No text selected")
        return "break"

    def show_context_menu(self, event):
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.geometry(f"150x82+{event.x_root}+{event.y_root}")
        menu.configure(fg_color="#101826")

        def close_menu():
            if menu.winfo_exists():
                menu.destroy()

        def copy_selected_cmd():
            self.copy_selected()
            close_menu()

        def copy_all_cmd():
            self.copy_callback(self.full_text)
            close_menu()

        btn1 = ctk.CTkButton(
            menu,
            text="Copy selected",
            height=32,
            corner_radius=10,
            fg_color="#22314c",
            hover_color="#2d4164",
            command=copy_selected_cmd
        )
        btn1.pack(fill="x", padx=8, pady=(8, 4))

        btn2 = ctk.CTkButton(
            menu,
            text="Copy all",
            height=32,
            corner_radius=10,
            fg_color="#22314c",
            hover_color="#2d4164",
            command=copy_all_cmd
        )
        btn2.pack(fill="x", padx=8, pady=(0, 8))

        menu.focus_force()
        menu.bind("<FocusOut>", lambda e: close_menu())


class TextBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("text.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("TextBridge")
        self.geometry("950x720")
        self.minsize(820, 560)

        self.ip = get_local_ip()
        self.messages = []
        self.is_topmost = False

        self.configure(fg_color="#0b1220")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        self.build_ui()
        self.poll_queue()

    def build_ui(self):
        self.outer = ctk.CTkFrame(self, fg_color="transparent")
        self.outer.pack(fill="both", expand=True, padx=18, pady=18)
        self.bind("<F9>", lambda e: self.toggle_topmost())

        # Header
        self.header = ctk.CTkFrame(self.outer, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 14))

        self.title_label = ctk.CTkLabel(
            self.header,
            text="TextBridge",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#f8fbff"
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header,
            text="Сообщения с Android появляются здесь и сразу копируются в clipboard.",
            font=ctk.CTkFont(size=20),
            text_color="#96a8c9"
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        # Top card
        self.info_card = ctk.CTkFrame(
            self.outer,
            corner_radius=20,
            fg_color="#10192b",
            border_width=1,
            border_color="#1f2c42"
        )
        self.info_card.pack(fill="x", pady=(0, 14))

        self.info_top = ctk.CTkFrame(self.info_card, fg_color="transparent")
        self.info_top.pack(fill="x", padx=16, pady=(16, 8))

        self.receiver_label = ctk.CTkLabel(
            self.info_top,
            text="Desktop receiver",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f5f9ff"
        )
        self.receiver_label.pack(side="left")

        self.buttons_wrap = ctk.CTkFrame(self.info_top, fg_color="transparent")
        self.buttons_wrap.pack(side="right")

        self.copy_ip_btn = ctk.CTkButton(
            self.buttons_wrap,
            text="Copy IP",
            width=95,
            height=36,
            corner_radius=12,
            fg_color="#2a5fff",
            hover_color="#2252e6",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.copy_text(self.ip)
        )
        self.copy_ip_btn.pack(side="left", padx=(0, 8))

        self.topmost_btn = ctk.CTkButton(
            self.buttons_wrap,
            text="Pin on top",
            width=110,
            height=36,
            corner_radius=12,
            fg_color="#22314c",
            hover_color="#2e456d",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.toggle_topmost
        )
        self.topmost_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            self.buttons_wrap,
            text="Clear",
            width=90,
            height=36,
            corner_radius=12,
            fg_color="#22314c",
            hover_color="#2e456d",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.clear_history
        )
        self.clear_btn.pack(side="left")

        self.url_label = ctk.CTkLabel(
            self.info_card,
            text=f"http://{self.ip}:5000",
            font=ctk.CTkFont(size=18, family="Consolas"),
            text_color="#7dd3fc"
        )
        self.url_label.pack(anchor="w", padx=16, pady=(0, 16))

        # Status
        self.status_var = ctk.StringVar(value=f"Listening on {self.ip}:5000")

        self.status_bar = ctk.CTkFrame(self.outer, fg_color="transparent")
        self.status_bar.pack(fill="x", pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=13),
            text_color="#96a8c9"
        )
        self.status_label.pack(side="left")

        # Messages area
        self.chat_card = ctk.CTkFrame(
            self.outer,
            corner_radius=22,
            fg_color="#0f1727",
            border_width=1,
            border_color="#1f2c42"
        )
        self.chat_card.pack(fill="both", expand=True)

        self.chat_scroll = ctk.CTkScrollableFrame(
            self.chat_card,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#31435f",
            scrollbar_button_hover_color="#425a7d"
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=12, pady=12)

        self.render_empty_state()

    def set_status(self, text):
        self.status_var.set(text)

    def copy_text(self, text):
        pyperclip.copy(text)
        self.set_status("Copied to clipboard")

    def clear_scroll_content(self):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

    def render_empty_state(self):
        self.clear_scroll_content()

        empty_card = ctk.CTkFrame(
            self.chat_scroll,
            corner_radius=18,
            fg_color="#10192b",
            border_width=1,
            border_color="#1f2c42"
        )
        empty_card.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(
            empty_card,
            text="Пока пусто",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f8fbff"
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            empty_card,
            text="Отправь текст с телефона — он появится здесь как красивое сообщение.",
            font=ctk.CTkFont(size=13),
            text_color="#96a8c9"
        ).pack(anchor="w", padx=16, pady=(0, 16))

    def render_messages(self):
        self.clear_scroll_content()

        for index, msg in enumerate(reversed(self.messages)):
            row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=8)

            is_latest = (index == 0)

            bubble = MessageBubble(
                row,
                text=msg["text"],
                time_text=msg["time"],
                copy_callback=self.copy_text,
                status_callback=self.set_status,
                is_latest=is_latest
            )

            bubble.pack(fill="x", padx=(0, 78 if is_latest else 10))

    def clear_history(self):
        self.messages.clear()
        self.render_empty_state()
        self.set_status("History cleared")

    def poll_queue(self):
        updated = False

        while not message_queue.empty():
            msg = message_queue.get()
            self.messages.append(msg)
            updated = True
            self.set_status("New text received and copied")

        if updated:
            self.render_messages()

        self.after(200, self.poll_queue)

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.attributes("-topmost", self.is_topmost)

        if self.is_topmost:
            self.topmost_btn.configure(
                text="Unpin",
                fg_color="#3b82f6",
                hover_color="#2563eb"
            )
            self.set_status("Window pinned on top")
        else:
            self.topmost_btn.configure(
                text="Pin on top",
                fg_color="#22314c",
                hover_color="#2e456d"
            )
            self.set_status("Window unpinned")

        if self.is_topmost:
            self.title("TextBridge 📌")
        else:
            self.title("TextBridge")


if __name__ == "__main__":
    app_ui = TextBridgeApp()
    app_ui.mainloop()
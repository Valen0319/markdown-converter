from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from converter import MarkdownConverter, SUPPORTED_EXTENSIONS


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"


class Settings:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.data = {
            "output_folder": str(BASE_DIR / "output"),
            "open_folder": True,
        }
        self.load()

    def load(self) -> None:
        if CONFIG_FILE.exists():
            try:
                saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                self.data.update(saved)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        CONFIG_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


COLORS = {
    "background": "#11140f",
    "panel": "#1a1f16",
    "panel_2": "#202719",
    "border": "#36412d",
    "olive": "#6f7f3a",
    "olive_hover": "#829347",
    "olive_light": "#a4b66a",
    "text": "#edf1e7",
    "muted": "#aab09f",
}


class MarkdownApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Conversor a Markdown")
        self.geometry("980x680")
        self.minsize(820, 560)
        self.configure(fg_color=COLORS["background"])

        self.settings = Settings()
        self.converter = MarkdownConverter()
        self.files: list[Path] = []
        self.event_queue: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None

        self._build_ui()
        self.output_entry.insert(0, self.settings.data["output_folder"])
        self.open_folder_var.set(bool(self.settings.data["open_folder"]))
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.after(100, self._poll_queue)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, fg_color=COLORS["panel"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(24, 18))
        ctk.CTkLabel(brand, text="MD", width=44, height=44, corner_radius=10,
                     fg_color=COLORS["olive"], text_color=COLORS["text"],
                     font=("Segoe UI", 18, "bold")).pack(side="left")
        ctk.CTkLabel(brand, text="Conversor\nMarkdown", justify="left",
                     text_color=COLORS["text"], font=("Segoe UI", 15, "bold")).pack(side="left", padx=12)

        ctk.CTkLabel(sidebar, text="ARCHIVOS", text_color=COLORS["olive_light"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(10, 8))

        self.add_button = self._sidebar_button("Agregar archivos", self._add_files)
        self.folder_button = self._sidebar_button("Agregar carpeta", self._add_folder)
        self.clear_button = self._sidebar_button("Limpiar lista", self._clear_files)

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=18, pady=18)
        ctk.CTkLabel(sidebar, text="SALIDA", text_color=COLORS["olive_light"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(0, 8))

        self.open_folder_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(sidebar, text="Abrir carpeta al terminar", variable=self.open_folder_var,
                        fg_color=COLORS["olive"], hover_color=COLORS["olive_hover"],
                        border_color=COLORS["olive_light"], text_color=COLORS["text"],
                        command=self._save_settings).pack(anchor="w", padx=22, pady=5)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(header, text="Convertir archivos", text_color=COLORS["text"],
                     font=("Segoe UI", 24, "bold")).pack(side="left")
        self.count_label = ctk.CTkLabel(header, text="0 archivos", text_color=COLORS["muted"],
                                        font=("Segoe UI", 13))
        self.count_label.pack(side="right")

        list_card = ctk.CTkFrame(main, fg_color=COLORS["panel"], corner_radius=12,
                                 border_width=1, border_color=COLORS["border"])
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.grid_rowconfigure(0, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        self.file_list = tk.Listbox(
            list_card, bg=COLORS["panel"], fg=COLORS["text"],
            selectbackground=COLORS["olive"], selectforeground="#ffffff",
            activestyle="none", borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 12), relief="flat"
        )
        self.file_list.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        empty = ctk.CTkLabel(list_card, text="Arrastra archivos aquí\nPDF · DOCX · XLSX · PPTX · HTML · TXT · Imágenes",
                             text_color=COLORS["muted"], font=("Segoe UI", 14), justify="center")
        empty.place(relx=.5, rely=.5, anchor="center")
        self.empty_label = empty

        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        bottom.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bottom, text="Carpeta de salida", text_color=COLORS["muted"],
                     font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=(0, 6))

        output_row = ctk.CTkFrame(bottom, fg_color="transparent")
        output_row.grid(row=1, column=0, sticky="ew")
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(output_row, height=42, fg_color=COLORS["panel"],
                                        border_color=COLORS["border"], text_color=COLORS["text"])
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(output_row, text="Examinar", width=110, height=42,
                      fg_color=COLORS["panel_2"], hover_color=COLORS["border"],
                      text_color=COLORS["text"], border_width=1,
                      border_color=COLORS["border"], command=self._choose_output).grid(row=0, column=1)

        self.progress = ctk.CTkProgressBar(bottom, height=8, fg_color=COLORS["border"],
                                           progress_color=COLORS["olive_light"])
        self.progress.grid(row=2, column=0, sticky="ew", pady=(14, 10))
        self.progress.set(0)

        status_row = ctk.CTkFrame(bottom, fg_color="transparent")
        status_row.grid(row=3, column=0, sticky="ew")
        status_row.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(status_row, text="Listo", text_color=COLORS["muted"])
        self.status_label.grid(row=0, column=0, sticky="w")

        self.convert_button = ctk.CTkButton(status_row, text="Convertir", width=150, height=44,
                                            fg_color=COLORS["olive"], hover_color=COLORS["olive_hover"],
                                            text_color="#ffffff", font=("Segoe UI", 13, "bold"),
                                            command=self._start_conversion)
        self.convert_button.grid(row=0, column=1)

        self._enable_drop_target()

    def _sidebar_button(self, text: str, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self.winfo_children()[0], text=text, height=40, anchor="w",
            fg_color=COLORS["panel"], hover_color=COLORS["panel_2"],
            text_color=COLORS["text"], border_width=1,
            border_color=COLORS["border"], corner_radius=8, command=command
        )
        button.pack(fill="x", padx=14, pady=4)
        return button

    def _enable_drop_target(self) -> None:
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            if not isinstance(self, TkinterDnD.DnDWrapper):
                self.file_list.drop_target_register(DND_FILES)
                self.file_list.dnd_bind("<<Drop>>", self._drop_files)
        except Exception:
            pass

    def _drop_files(self, event) -> None:
        paths = self.tk.splitlist(event.data)
        self._add_paths(paths)

    def _add_files(self) -> None:
        file_types = [("Archivos admitidos", " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))), ("Todos", "*.*")]
        paths = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=file_types)
        self._add_paths(paths)

    def _add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            paths = [str(path) for path in Path(folder).rglob("*") if path.is_file()]
            self._add_paths(paths)

    def _add_paths(self, paths) -> None:
        for value in paths:
            path = Path(value.strip('{}'))
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                if path not in self.files:
                    self.files.append(path)
        self._refresh_file_list()

    def _clear_files(self) -> None:
        self.files.clear()
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        self.file_list.delete(0, tk.END)
        for path in self.files:
            self.file_list.insert(tk.END, f"  {path.name}   —   {path.parent}")
        self.count_label.configure(text=f"{len(self.files)} archivo{'s' if len(self.files) != 1 else ''}")
        self.empty_label.place_forget() if self.files else self.empty_label.place(relx=.5, rely=.5, anchor="center")

    def _choose_output(self) -> None:
        folder = filedialog.askdirectory(initialdir=self.output_entry.get(), title="Elegir carpeta de salida")
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self._save_settings()

    def _save_settings(self) -> None:
        self.settings.data["output_folder"] = self.output_entry.get() if hasattr(self, "output_entry") else self.settings.data["output_folder"]
        self.settings.data["open_folder"] = self.open_folder_var.get() if hasattr(self, "open_folder_var") else True
        self.settings.save()

    def _start_conversion(self) -> None:
        if not self.files:
            messagebox.showwarning("Sin archivos", "Agrega al menos un archivo para convertir.")
            return

        output = self.output_entry.get().strip()
        if not output:
            messagebox.showwarning("Carpeta requerida", "Selecciona una carpeta de salida.")
            return

        self._save_settings()
        self.convert_button.configure(state="disabled", text="Convirtiendo...")
        self.progress.set(0)

        files = list(self.files)
        self.worker = threading.Thread(target=self._conversion_worker, args=(files, output), daemon=True)
        self.worker.start()

    def _conversion_worker(self, files: list[Path], output: str) -> None:
        output_folder = Path(output)

        def progress(done: int, total: int, name: str) -> None:
            self.event_queue.put(("progress", done / total, f"{name}  ·  {done}/{total}"))

        successful, errors = self.converter.convert_many(files, output_folder, progress)
        self.event_queue.put(("done", successful, errors, output_folder))

    def _poll_queue(self) -> None:
        try:
            while True:
                event = self.event_queue.get_nowait()
                kind = event[0]
                if kind == "progress":
                    self.progress.set(event[1])
                    self.status_label.configure(text=event[2])
                elif kind == "done":
                    successful, errors, output_folder = event[1:]
                    self.progress.set(1)
                    self.convert_button.configure(state="normal", text="Convertir")
                    self.status_label.configure(text=f"{len(successful)} convertidos · {len(errors)} errores")
                    if errors:
                        messagebox.showwarning("Conversión completada", "\n".join(errors[:8]))
                    elif successful:
                        messagebox.showinfo("Conversión completada", f"Se convirtieron {len(successful)} archivo(s).")
                    if successful and self.open_folder_var.get():
                        self._open_folder(output_folder)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    @staticmethod
    def _open_folder(folder: Path) -> None:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)], check=False)
            else:
                subprocess.run(["xdg-open", str(folder)], check=False)
        except OSError:
            pass

    def _on_close(self) -> None:
        self._save_settings()
        self.destroy()


if __name__ == "__main__":
    app = MarkdownApp()
    app.mainloop()

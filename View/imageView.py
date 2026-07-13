from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from pathlib import Path
from Controller.imageController import ImageController

APP_BG = "#0f1117"
PANEL = "#171a23"
PANEL_ALT = "#1f2430"
BORDER = "#2f3545"
TEXT = "#f8fafc"
MUTED = "#9aa4b2"
PRIMARY = "#3b82f6"
PRIMARY_HOVER = "#2563eb"
SUCCESS = "#22c55e"
SUCCESS_HOVER = "#16a34a"

class ScriptImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("ScriptImage")
        self.geometry("1180x760")
        self.minsize(1040, 680)
        self.configure(fg_color=APP_BG)

        self.controller = ImageController(self)
        self.preview_original = None
        self.preview_result = None
        self.current_mode = "color"

        self._build_layout()
        self.switch_mode("color")

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(self.header, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=18, pady=10)
        ctk.CTkLabel(brand, text="ScriptImage", font=("Segoe UI", 24, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(brand, text="Editor, conversor e otimizador de imagens", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="w")
        ctk.CTkLabel(brand, text="GitHub: tiagolucasoo", font=("Segoe UI", 12), text_color=MUTED).pack(anchor="w")

        nav = ctk.CTkFrame(self.header, fg_color="transparent")
        nav.grid(row=0, column=1, sticky="e", padx=18)
        self.btn_color = self._top_button(nav, "Substituir cor", lambda: self.switch_mode("color"))
        self.btn_convert = self._top_button(nav, "Converter", lambda: self.switch_mode("convert"))
        self.btn_optimize = self._top_button(nav, "Otimizar", lambda: self.switch_mode("optimize"))

        self.config_bar = ctk.CTkFrame(self, fg_color=PANEL_ALT, border_width=1, border_color=BORDER, corner_radius=8)
        self.config_bar.grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 10))
        self.config_bar.grid_columnconfigure(0, weight=1)

        self.preview = ctk.CTkFrame(self, fg_color=PANEL, border_color=BORDER, border_width=1, corner_radius=8)
        self.preview.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 14))
        self.preview.grid_columnconfigure((0, 1), weight=1)
        self.preview.grid_rowconfigure(1, weight=1)

        self.left_title = ctk.CTkLabel(self.preview, text="Original", font=("Segoe UI", 18, "bold"), text_color=TEXT)
        self.left_title.grid(
            row=0, column=0, sticky="w", padx=18, pady=(16, 10)
        )
        self.right_title = ctk.CTkLabel(self.preview, text="Resultado", font=("Segoe UI", 18, "bold"), text_color=TEXT)
        self.right_title.grid(
            row=0, column=1, sticky="w", padx=18, pady=(16, 10)
        )
        self.original_box = ctk.CTkLabel(
            self.preview,
            text="Carregue uma imagem",
            text_color=MUTED,
            fg_color="#10141d",
            corner_radius=8,
        )
        self.original_box.grid(row=1, column=0, sticky="nsew", padx=(18, 8), pady=(0, 18))
        self.result_box = ctk.CTkLabel(
            self.preview,
            text="Aguardando resultado",
            text_color=MUTED,
            fg_color="#10141d",
            corner_radius=8,
        )
        self.result_box.grid(row=1, column=1, sticky="nsew", padx=(8, 18), pady=(0, 18))

        self.status_label = ctk.CTkLabel(self.preview, text="Pronto.", text_color=MUTED, font=("Segoe UI", 11))
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))

    def _top_button(self, parent, text, command):
        button = ctk.CTkButton(parent, text=text, height=36, width=136, fg_color="transparent", hover_color="#243044", command=command)
        button.pack(side="left", padx=4)
        return button

    def switch_mode(self, mode: str):
        self.current_mode = mode
        for widget in self.config_bar.winfo_children():
            widget.destroy()
        self._style_nav()
        if mode == "color":
            self._show_preview_area()
            self._build_color_bar()
        elif mode == "convert":
            self._show_preview_area()
            self._build_convert_bar()
        else:
            self._show_optimize_area()
            self._build_optimize_bar()

    def _style_nav(self):
        mapping = {"color": self.btn_color, "convert": self.btn_convert, "optimize": self.btn_optimize}
        for mode, button in mapping.items():
            button.configure(fg_color=PRIMARY if mode == self.current_mode else "transparent")

    def _show_preview_area(self):
        if hasattr(self, "optimize_file_panel"):
            self.optimize_file_panel.grid_remove()
            self.optimize_result_panel.grid_remove()
        self.left_title.configure(text="Original")
        self.right_title.configure(text="Resultado")
        self.original_box.grid(row=1, column=0, sticky="nsew", padx=(18, 8), pady=(0, 18))
        self.result_box.grid(row=1, column=1, sticky="nsew", padx=(8, 18), pady=(0, 18))

    def _show_optimize_area(self):
        self.original_box.grid_remove()
        self.result_box.grid_remove()
        self.left_title.configure(text="Arquivos")
        self.right_title.configure(text="Antes / depois")

        if not hasattr(self, "optimize_file_panel"):
            self.optimize_file_panel = ctk.CTkScrollableFrame(self.preview, fg_color="#10141d", corner_radius=8)
            self.optimize_result_panel = ctk.CTkFrame(self.preview, fg_color="#10141d", corner_radius=8)
            self.optimize_result_panel.grid_columnconfigure(0, weight=1)
            self.optimize_result_label = ctk.CTkLabel(
                self.optimize_result_panel,
                text="Carregue arquivos ou uma pasta. Todos entram marcados por padrao.",
                text_color=MUTED,
                font=("Segoe UI", 13),
                wraplength=430,
                justify="left",
            )
            self.optimize_result_label.grid(row=0, column=0, sticky="nw", padx=18, pady=18)
            self.optimize_files = []
            self.optimize_file_vars = []

        self.optimize_file_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 8), pady=(0, 18))
        self.optimize_result_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 18), pady=(0, 18))

    def set_optimization_files(self, files):
        self._show_optimize_area()
        self.optimize_files = [Path(path) for path in files]
        self.optimize_file_vars = []

        for widget in self.optimize_file_panel.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.optimize_file_panel, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 6))
        ctk.CTkLabel(header, text=f"{len(self.optimize_files)} arquivo(s)", text_color=TEXT, font=("Segoe UI", 13, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Todos", width=66, height=28, command=lambda: self._set_all_optimization_checks(True)).pack(side="right", padx=(6, 0))
        ctk.CTkButton(header, text="Nenhum", width=76, height=28, fg_color="#334155", hover_color="#475569", command=lambda: self._set_all_optimization_checks(False)).pack(side="right")

        for path in self.optimize_files:
            var = ctk.BooleanVar(value=True)
            self.optimize_file_vars.append(var)
            size = self.controller._format_bytes(path.stat().st_size) if path.exists() else "0 B"
            checkbox = ctk.CTkCheckBox(
                self.optimize_file_panel,
                text=f"{path.name}  |  {size}",
                variable=var,
                text_color="#dbe4f0",
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
            )
            checkbox.pack(fill="x", padx=10, pady=4, anchor="w")

        self.optimize_result_label.configure(text="Arquivos carregados. Desmarque o que nao quiser otimizar e clique em Otimizar selecionados.")

    def _set_all_optimization_checks(self, value: bool):
        for var in getattr(self, "optimize_file_vars", []):
            var.set(value)

    def get_selected_optimization_files(self):
        return [
            path
            for path, var in zip(getattr(self, "optimize_files", []), getattr(self, "optimize_file_vars", []))
            if var.get()
        ]

    def _label(self, parent, text):
        return ctk.CTkLabel(parent, text=text, text_color=TEXT, font=("Segoe UI", 11, "bold"))

    def _build_color_bar(self):
        row = self._config_row()
        ctk.CTkButton(row, text="Carregar imagem", width=132, height=34, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=self.controller.load_single_image).grid(row=0, column=0, padx=(0, 10))

        self._label(row, "Cor original").grid(row=0, column=1, padx=(0, 6))
        self.old_color = ctk.CTkComboBox(row, values=["#000000"], width=118, height=34)
        self.old_color.grid(row=0, column=2, padx=(0, 6))
        self.old_swatch = ctk.CTkFrame(row, width=32, height=32, fg_color="#000000", corner_radius=6)
        self.old_swatch.grid(row=0, column=3, padx=(0, 12))
        self.old_color.configure(command=lambda value: self.old_swatch.configure(fg_color=value))

        self._label(row, "Nova cor").grid(row=0, column=4, padx=(0, 6))
        self.new_color_var = ctk.StringVar(value="#000000")
        self.new_color_var.trace_add("write", lambda *_: self._sync_new_swatch())
        self.new_color = ctk.CTkEntry(row, textvariable=self.new_color_var, width=104, height=34)
        self.new_color.grid(row=0, column=5, padx=(0, 6))
        self.new_swatch = ctk.CTkFrame(row, width=32, height=32, fg_color="#000000", corner_radius=6)
        self.new_swatch.grid(row=0, column=6, padx=(0, 12))

        self._label(row, "Tolerancia").grid(row=0, column=7, padx=(0, 6))
        self.tolerance = ctk.CTkSlider(row, from_=0, to=150, number_of_steps=150, width=130)
        self.tolerance.set(40)
        self.tolerance.grid(row=0, column=8, padx=(0, 12))

        ctk.CTkButton(
            row,
            text="Gerar previa",
            width=112,
            height=34,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            command=lambda: self.controller.generate_recolor_preview(self.old_color.get(), self.new_color_var.get(), int(self.tolerance.get())),
        ).grid(row=0, column=9, padx=(0, 8))
        ctk.CTkButton(row, text="Salvar", width=82, height=34, command=self.controller.save_result).grid(row=0, column=10)

    def _build_convert_bar(self):
        row = self._config_row()
        ctk.CTkButton(row, text="Carregar imagem", width=132, height=34, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=self.controller.load_single_image).grid(row=0, column=0, padx=(0, 12))
        self._label(row, "Formato").grid(row=0, column=1, padx=(0, 6))
        self.convert_format = ctk.CTkOptionMenu(row, values=["PNG", "JPEG", "WEBP"], width=110, height=34)
        self.convert_format.set("PNG")
        self.convert_format.grid(row=0, column=2, padx=(0, 12))
        self._label(row, "Qualidade").grid(row=0, column=3, padx=(0, 6))
        self.convert_quality = ctk.CTkSlider(row, from_=40, to=100, number_of_steps=60, width=160)
        self.convert_quality.set(90)
        self.convert_quality.grid(row=0, column=4, padx=(0, 12))
        ctk.CTkButton(
            row,
            text="Converter e salvar",
            width=140,
            height=34,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            command=lambda: self.controller.convert_current(self.convert_format.get(), int(self.convert_quality.get())),
        ).grid(row=0, column=5)

    def _build_optimize_bar(self):
        row1 = self._config_row(row_index=0, pady=(12, 6))
        row2 = self._config_row(row_index=1, pady=(0, 12))
        self.last_output_dir = None

        self._label(row1, "Formato").grid(row=0, column=0, padx=(0, 6))
        self.optimize_format = ctk.CTkOptionMenu(row1, values=["JPEG", "PNG", "WEBP"], width=104, height=34)
        self.optimize_format.set("WEBP")
        self.optimize_format.grid(row=0, column=1, padx=(0, 12))

        self._label(row1, "Qualidade").grid(row=0, column=2, padx=(0, 6))
        self.optimize_quality = ctk.CTkSlider(row1, from_=40, to=100, number_of_steps=60, width=150)
        self.optimize_quality.set(82)
        self.optimize_quality.grid(row=0, column=3, padx=(0, 14))

        self._label(row1, "Redimensionar por").grid(row=0, column=4, padx=(0, 6))
        self.resize_mode = ctk.CTkOptionMenu(
            row1,
            values=["Largura maxima", "Altura maxima", "Porcentagem", "Maximo de pixels", "Tamanho exato", "Nao redimensionar"],
            width=174,
            height=34,
            command=lambda _: self._sync_optimize_fields(),
        )
        self.resize_mode.set("Largura maxima")
        self.resize_mode.grid(row=0, column=5, padx=(0, 12))

        self.keep_ratio_var = ctk.BooleanVar(value=True)
        self.keep_ratio = ctk.CTkCheckBox(row1, text="Manter proporcao", variable=self.keep_ratio_var, width=136)
        self.keep_ratio.grid(row=0, column=6)

        self._label(row2, "Largura").grid(row=0, column=0, padx=(0, 6))
        self.max_width = ctk.CTkEntry(row2, width=86, height=34)
        self.max_width.insert(0, "1600")
        self.max_width.grid(row=0, column=1, padx=(0, 12))

        self._label(row2, "Altura").grid(row=0, column=2, padx=(0, 6))
        self.max_height = ctk.CTkEntry(row2, width=86, height=34)
        self.max_height.insert(0, "1200")
        self.max_height.grid(row=0, column=3, padx=(0, 12))

        self._label(row2, "%").grid(row=0, column=4, padx=(0, 6))
        self.percent = ctk.CTkEntry(row2, width=70, height=34)
        self.percent.insert(0, "80")
        self.percent.grid(row=0, column=5, padx=(0, 12))

        self._label(row2, "Max pixels").grid(row=0, column=6, padx=(0, 6))
        self.max_pixels = ctk.CTkEntry(row2, width=108, height=34)
        self.max_pixels.insert(0, "2000000")
        self.max_pixels.grid(row=0, column=7, padx=(0, 12))

        ctk.CTkButton(
            row2,
            text="Carregar arquivos",
            width=124,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("files"),
        ).grid(row=0, column=8, padx=(0, 8))
        ctk.CTkButton(
            row2,
            text="Carregar pasta",
            width=112,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("folder"),
        ).grid(row=0, column=9, padx=(0, 8))
        ctk.CTkButton(
            row2,
            text="Otimizar selecionados",
            width=154,
            height=34,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            command=self._optimize_from_view,
        ).grid(row=0, column=10, padx=(0, 8))
        ctk.CTkButton(
            row2,
            text="Abrir saida",
            width=96,
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            command=lambda: self.controller.open_output_folder(self.last_output_dir),
        ).grid(row=0, column=11)

        self.optimize_summary = ctk.CTkLabel(
            self.config_bar,
            text="Antes/depois aparece aqui apos otimizar.",
            text_color=MUTED,
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.optimize_summary.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        self._sync_optimize_fields()

    def _config_row(self, row_index=0, pady=12):
        row = ctk.CTkFrame(self.config_bar, fg_color="transparent")
        row.grid(row=row_index, column=0, sticky="w", padx=14, pady=pady)
        return row

    def _sync_optimize_fields(self):
        mode = self.resize_mode.get()
        disabled = "disabled"
        normal = "normal"
        self.max_width.configure(state=normal if mode in {"Largura maxima", "Tamanho exato"} else disabled)
        self.max_height.configure(state=normal if mode in {"Altura maxima", "Tamanho exato"} else disabled)
        self.percent.configure(state=normal if mode == "Porcentagem" else disabled)
        self.max_pixels.configure(state=normal if mode == "Maximo de pixels" else disabled)
        self.keep_ratio.configure(state=normal if mode == "Tamanho exato" else disabled)

    def _optimize_from_view(self):
        try:
            options = {
                "mode": self.resize_mode.get(),
                "max_width": int(self.max_width.get().strip() or "0"),
                "max_height": int(self.max_height.get().strip() or "0"),
                "percent": int(self.percent.get().strip() or "100"),
                "max_pixels": int(self.max_pixels.get().strip() or "0"),
                "target_width": int(self.max_width.get().strip() or "0"),
                "target_height": int(self.max_height.get().strip() or "0"),
                "keep_ratio": self.keep_ratio_var.get(),
            }
        except ValueError:
            messagebox.showerror("Erro", "Os campos de tamanho precisam ser numericos.")
            return
        self.controller.optimize_selected_files(
            self.get_selected_optimization_files(),
            options,
            int(self.optimize_quality.get()),
            self.optimize_format.get(),
        )

    def set_optimization_summary(self, text: str):
        if hasattr(self, "optimize_summary"):
            self.optimize_summary.configure(text=text)
        if hasattr(self, "optimize_result_label"):
            self.optimize_result_label.configure(text=text)

    def _sync_new_swatch(self):
        value = self.new_color_var.get()
        if self.controller.service.is_hex(value):
            self.new_swatch.configure(fg_color=value)

    def _build_optimize_bar(self):
        self.last_output_dir = None
        self.optimize_summary = None

        row1 = self._config_row(row_index=0, pady=(12, 6))
        row2 = self._config_row(row_index=1, pady=(0, 10))

        ctk.CTkButton(
            row1,
            text="Arquivos",
            width=92,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("files"),
        ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            row1,
            text="Pasta",
            width=78,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("folder"),
        ).grid(row=0, column=1, padx=(0, 14))

        self._label(row1, "Saida").grid(row=0, column=2, padx=(0, 6))
        self.output_dir_label = ctk.CTkLabel(
            row1,
            text="Nao definida",
            width=230,
            height=34,
            fg_color="#111827",
            corner_radius=6,
            text_color=MUTED,
            anchor="w",
        )
        self.output_dir_label.grid(row=0, column=3, padx=(0, 8))
        ctk.CTkButton(
            row1,
            text="Escolher",
            width=84,
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            command=self._choose_output_dir,
        ).grid(row=0, column=4, padx=(0, 14))

        self._label(row1, "Formato").grid(row=0, column=5, padx=(0, 6))
        self.optimize_format = ctk.CTkOptionMenu(row1, values=["JPEG", "PNG", "WEBP"], width=96, height=34)
        self.optimize_format.set("WEBP")
        self.optimize_format.grid(row=0, column=6, padx=(0, 12))

        self._label(row1, "Qualidade").grid(row=0, column=7, padx=(0, 6))
        self.optimize_quality = ctk.CTkSlider(row1, from_=40, to=100, number_of_steps=60, width=130)
        self.optimize_quality.set(82)
        self.optimize_quality.grid(row=0, column=8)

        self._label(row2, "Redimensionar").grid(row=0, column=0, padx=(0, 6))
        self.resize_mode = ctk.CTkOptionMenu(
            row2,
            values=["Largura maxima", "Altura maxima", "Porcentagem", "Maximo de pixels", "Tamanho exato", "Nao redimensionar"],
            width=170,
            height=34,
            command=lambda _: self._sync_optimize_fields(),
        )
        self.resize_mode.set("Largura maxima")
        self.resize_mode.grid(row=0, column=1, padx=(0, 12))

        self.value_label = self._label(row2, "Valor")
        self.value_label.grid(row=0, column=2, padx=(0, 6))
        self.resize_value = ctk.CTkEntry(row2, width=92, height=34)
        self.resize_value.insert(0, "1600")
        self.resize_value.grid(row=0, column=3, padx=(0, 8))

        self.second_value_label = self._label(row2, "Altura")
        self.second_value_label.grid(row=0, column=4, padx=(0, 6))
        self.resize_value_2 = ctk.CTkEntry(row2, width=92, height=34)
        self.resize_value_2.insert(0, "1200")
        self.resize_value_2.grid(row=0, column=5, padx=(0, 10))

        self.keep_ratio_var = ctk.BooleanVar(value=True)
        self.keep_ratio = ctk.CTkCheckBox(row2, text="Manter proporcao", variable=self.keep_ratio_var, width=136)
        self.keep_ratio.grid(row=0, column=6, padx=(0, 14))

        ctk.CTkButton(
            row2,
            text="Otimizar selecionados",
            width=164,
            height=34,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            command=self._optimize_from_view,
        ).grid(row=0, column=7, padx=(0, 8))
        ctk.CTkButton(
            row2,
            text="Abrir saida",
            width=96,
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            command=lambda: self.controller.open_output_folder(self.last_output_dir),
        ).grid(row=0, column=8)

        self.optimize_summary = ctk.CTkLabel(
            self.config_bar,
            text="Carregue arquivos ou uma pasta, desmarque o que quiser e otimize os selecionados.",
            text_color=MUTED,
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.optimize_summary.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        self._sync_optimize_fields()

    def _choose_output_dir(self):
        output_dir = filedialog.askdirectory(title="Escolha a pasta de saida")
        if not output_dir:
            return
        self.last_output_dir = output_dir
        display = output_dir if len(output_dir) <= 38 else "..." + output_dir[-35:]
        self.output_dir_label.configure(text=display, text_color=TEXT)

    def set_default_output_dir(self, files):
        if not files or not hasattr(self, "output_dir_label"):
            return
        parent = Path(files[0]).parent
        output_dir = parent / "otimizadas"
        self.last_output_dir = str(output_dir)
        display = str(output_dir)
        display = display if len(display) <= 38 else "..." + display[-35:]
        self.output_dir_label.configure(text=display, text_color=TEXT)

    def _sync_optimize_fields(self):
        mode = self.resize_mode.get()
        normal = "normal"
        disabled = "disabled"

        labels = {
            "Largura maxima": ("Largura", "1600"),
            "Altura maxima": ("Altura", "1200"),
            "Porcentagem": ("%", "80"),
            "Maximo de pixels": ("Pixels", "2000000"),
            "Tamanho exato": ("Largura", "1600"),
            "Nao redimensionar": ("Valor", ""),
        }
        label, default = labels.get(mode, ("Valor", ""))
        self.value_label.configure(text=label)
        self.resize_value.configure(state=normal if mode != "Nao redimensionar" else disabled)
        if default and not self.resize_value.get().strip():
            self.resize_value.insert(0, default)

        exact = mode == "Tamanho exato"
        self.second_value_label.configure(text="Altura")
        self.resize_value_2.configure(state=normal if exact else disabled)
        self.keep_ratio.configure(state=normal if exact else disabled)

    def _optimize_options_from_view(self):
        mode = self.resize_mode.get()
        value = self.resize_value.get().strip()
        value2 = self.resize_value_2.get().strip()

        def number(raw, fallback=0):
            return int(raw or fallback)

        options = {
            "mode": mode,
            "max_width": 0,
            "max_height": 0,
            "percent": 100,
            "max_pixels": 0,
            "target_width": 0,
            "target_height": 0,
            "keep_ratio": self.keep_ratio_var.get(),
        }
        if mode == "Largura maxima":
            options["max_width"] = number(value)
        elif mode == "Altura maxima":
            options["max_height"] = number(value)
        elif mode == "Porcentagem":
            options["percent"] = number(value, 100)
        elif mode == "Maximo de pixels":
            options["max_pixels"] = number(value)
        elif mode == "Tamanho exato":
            options["target_width"] = number(value)
            options["target_height"] = number(value2)
        return options

    def _optimize_from_view(self):
        try:
            options = self._optimize_options_from_view()
        except ValueError:
            messagebox.showerror("Erro", "Os campos de tamanho precisam ser numericos.")
            return
        self.controller.optimize_selected_files(
            self.get_selected_optimization_files(),
            options,
            int(self.optimize_quality.get()),
            self.optimize_format.get(),
            self.last_output_dir,
        )

    def _build_optimize_bar(self):
        self.last_output_dir = None
        self.config_bar.grid_columnconfigure(0, weight=0)
        self.config_bar.grid_columnconfigure(1, weight=1)

        origin_card = ctk.CTkFrame(self.config_bar, fg_color="#151923", border_color=BORDER, border_width=1, corner_radius=8)
        origin_card.grid(row=0, column=0, sticky="nsew", padx=(14, 8), pady=12)
        settings_card = ctk.CTkFrame(self.config_bar, fg_color="#151923", border_color=BORDER, border_width=1, corner_radius=8)
        settings_card.grid(row=0, column=1, sticky="nsew", padx=(8, 14), pady=12)

        ctk.CTkLabel(origin_card, text="Origem", text_color=TEXT, font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6)
        )
        ctk.CTkButton(
            origin_card,
            text="Arquivo",
            width=96,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("files"),
        ).grid(row=1, column=0, padx=(12, 6), pady=(0, 8))
        ctk.CTkButton(
            origin_card,
            text="Pasta",
            width=88,
            height=34,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=lambda: self.controller.select_optimization_sources("folder"),
        ).grid(row=1, column=1, padx=(0, 12), pady=(0, 8))
        ctk.CTkLabel(
            origin_card,
            text="Carregue os arquivos e desmarque na lista abaixo o que nao quiser otimizar.",
            text_color=MUTED,
            font=("Segoe UI", 11),
            wraplength=210,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        settings_card.grid_columnconfigure(1, weight=1)
        settings_card.grid_columnconfigure(3, weight=1)
        self._label(settings_card, "Formato").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 8))
        self.optimize_format = ctk.CTkOptionMenu(settings_card, values=["JPEG", "PNG", "WEBP"], width=112, height=34)
        self.optimize_format.set("WEBP")
        self.optimize_format.grid(row=0, column=1, sticky="w", padx=(0, 18), pady=(10, 8))

        self._label(settings_card, "Qualidade").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=(10, 8))
        self.optimize_quality = ctk.CTkSlider(settings_card, from_=40, to=100, number_of_steps=60, width=190)
        self.optimize_quality.set(82)
        self.optimize_quality.configure(command=lambda value: self._update_optimize_quality_label(value))
        self.optimize_quality.grid(row=0, column=3, sticky="ew", padx=(0, 8), pady=(10, 8))
        self.optimize_quality_label = ctk.CTkLabel(
            settings_card,
            text="82%",
            width=44,
            text_color=MUTED,
            font=("Segoe UI", 11, "bold"),
        )
        self.optimize_quality_label.grid(row=0, column=4, sticky="w", padx=(0, 12), pady=(10, 8))

        self._label(settings_card, "Redimensionar").grid(row=1, column=0, sticky="w", padx=(12, 6), pady=(0, 8))
        self.resize_mode = ctk.CTkOptionMenu(
            settings_card,
            values=["Largura maxima", "Altura maxima", "Porcentagem", "Maximo de pixels", "Tamanho exato", "Nao redimensionar"],
            width=170,
            height=34,
            command=lambda _: self._sync_optimize_fields(),
        )
        self.resize_mode.set("Largura maxima")
        self.resize_mode.grid(row=1, column=1, sticky="w", padx=(0, 18), pady=(0, 8))

        self.keep_ratio_var = ctk.BooleanVar(value=True)
        self.keep_ratio = ctk.CTkCheckBox(settings_card, text="Manter proporcao", variable=self.keep_ratio_var, width=140)
        self.keep_ratio.grid(row=1, column=2, columnspan=2, sticky="w", padx=(0, 12), pady=(0, 8))

        self.value_label = self._label(settings_card, "Valor")
        self.value_label.grid(row=2, column=0, sticky="w", padx=(12, 6), pady=(0, 10))
        self.resize_value = ctk.CTkEntry(settings_card, width=112, height=34)
        self.resize_value.insert(0, "1600")
        self.resize_value.grid(row=2, column=1, sticky="w", padx=(0, 18), pady=(0, 10))

        self.second_value_label = self._label(settings_card, "Altura")
        self.second_value_label.grid(row=2, column=2, sticky="w", padx=(0, 6), pady=(0, 10))
        self.resize_value_2 = ctk.CTkEntry(settings_card, width=112, height=34)
        self.resize_value_2.insert(0, "1200")
        self.resize_value_2.grid(row=2, column=3, sticky="w", padx=(0, 12), pady=(0, 10))

        self.optimize_summary = ctk.CTkLabel(
            self.config_bar,
            text="Saida automatica: pasta 'otimizadas' ao lado dos arquivos carregados.",
            text_color=MUTED,
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.optimize_summary.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))
        self._sync_optimize_fields()

    def _update_optimize_quality_label(self, value):
        if hasattr(self, "optimize_quality_label"):
            self.optimize_quality_label.configure(text=f"{int(float(value))}%")

    def set_optimization_files(self, files):
        self._show_optimize_area()
        self.optimize_files = [Path(path) for path in files]
        self.optimize_file_vars = []

        for widget in self.optimize_file_panel.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.optimize_file_panel, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 6))
        ctk.CTkLabel(header, text=f"{len(self.optimize_files)} arquivo(s)", text_color=TEXT, font=("Segoe UI", 13, "bold")).pack(side="left")
        ctk.CTkButton(
            header,
            text="Otimizar selecionados",
            width=152,
            height=28,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            command=self._optimize_from_view,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(header, text="Todos", width=66, height=28, command=lambda: self._set_all_optimization_checks(True)).pack(side="right", padx=(6, 0))
        ctk.CTkButton(header, text="Nenhum", width=76, height=28, fg_color="#334155", hover_color="#475569", command=lambda: self._set_all_optimization_checks(False)).pack(side="right")

        for path in self.optimize_files:
            var = ctk.BooleanVar(value=True)
            self.optimize_file_vars.append(var)
            size = self.controller._format_bytes(path.stat().st_size) if path.exists() else "0 B"
            checkbox = ctk.CTkCheckBox(
                self.optimize_file_panel,
                text=f"{path.name}  |  {size}",
                variable=var,
                text_color="#dbe4f0",
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
            )
            checkbox.pack(fill="x", padx=10, pady=4, anchor="w")

        self.optimize_result_label.configure(text="Arquivos carregados. A saida sera criada automaticamente na pasta 'otimizadas'.")

    def set_default_output_dir(self, files):
        if not files:
            return
        self.last_output_dir = str(Path(files[0]).parent / "otimizadas")
        if hasattr(self, "optimize_summary"):
            self.optimize_summary.configure(text=f"Saida automatica: {self.last_output_dir}")

    def _sync_optimize_fields(self):
        mode = self.resize_mode.get()
        normal = "normal"
        disabled = "disabled"

        labels = {
            "Largura maxima": ("Largura", "1600"),
            "Altura maxima": ("Altura", "1200"),
            "Porcentagem": ("%", "80"),
            "Maximo de pixels": ("Pixels", "2000000"),
            "Tamanho exato": ("Largura", "1600"),
            "Nao redimensionar": ("Valor", ""),
        }
        label, default = labels.get(mode, ("Valor", ""))
        self.value_label.configure(text=label)
        self.resize_value.configure(state=normal if mode != "Nao redimensionar" else disabled)
        if default:
            self.resize_value.delete(0, "end")
            self.resize_value.insert(0, default)

        exact = mode == "Tamanho exato"
        self.second_value_label.configure(text="Altura")
        self.resize_value_2.configure(state=normal if exact else disabled)
        self.keep_ratio.configure(state=normal if exact else disabled)

    def set_color_options(self, colors: list[str]):
        colors = colors or ["#000000"]
        if hasattr(self, "old_color"):
            self.old_color.configure(values=colors)
            self.old_color.set(colors[0])
            self.old_swatch.configure(fg_color=colors[0])

    def show_preview(self, original: Image.Image | None, result: Image.Image | None):
        if original:
            preview = self.controller.service.resize_for_preview(original, 560)
            self.preview_original = ctk.CTkImage(light_image=preview, dark_image=preview, size=preview.size)
            self.original_box.configure(image=self.preview_original, text="")
        if result:
            preview = self.controller.service.resize_for_preview(result, 560)
            self.preview_result = ctk.CTkImage(light_image=preview, dark_image=preview, size=preview.size)
            self.result_box.configure(image=self.preview_result, text="")
        else:
            self.result_box.configure(image=None, text="Aguardando resultado")

    def set_status(self, text: str):
        self.status_label.configure(text=text)
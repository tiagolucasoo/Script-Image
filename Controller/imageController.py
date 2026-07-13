import os
from pathlib import Path
from Service.imageService import ImageService
from Service.imageService import ImageDocument
from tkinter import filedialog, messagebox

class ImageController:
    def __init__(self, view):
        self.view = view
        self.service = ImageService()
        self.doc = ImageDocument(dominant_colors=[])

    def load_single_image(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Imagens", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.svg"),
                ("Todos os arquivos", "*.*"),
            ]
        )
        if not path:
            return
        try:
            image = self.service.load_image(path)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return

        self.doc = ImageDocument(path=Path(path), original=image, result=None)
        self.doc.dominant_colors = self.service.dominant_colors(image)
        self.view.set_status(f"Imagem carregada: {Path(path).name}")
        self.view.show_preview(image, None)
        self.view.set_color_options(self.doc.dominant_colors)

    def generate_recolor_preview(self, old_color: str, new_color: str, tolerance: int):
        if not self.doc.original:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return
        try:
            self.doc.result = self.service.replace_color(self.doc.original, old_color, new_color, tolerance)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.view.show_preview(self.doc.original, self.doc.result)
        self.view.set_status("Previa gerada.")

    def save_result(self, default_suffix: str = ".png"):
        if not self.doc.result:
            messagebox.showwarning("Aviso", "Gere uma previa primeiro.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=default_suffix,
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("WEBP", "*.webp"),
            ],
        )
        if not path:
            return
        fmt = Path(path).suffix.lower().lstrip(".") or "png"
        try:
            self.service.convert_image(self.doc.result, path, fmt)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.view.set_status(f"Arquivo salvo: {Path(path).name}")

    def convert_current(self, fmt: str, quality: int):
        if not self.doc.original:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return
        ext = ".jpg" if fmt.upper() in {"JPG", "JPEG"} else f".{fmt.lower()}"
        path = filedialog.asksaveasfilename(defaultextension=ext)
        if not path:
            return
        try:
            self.service.convert_image(self.doc.original, path, fmt, quality)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.view.set_status(f"Convertido: {Path(path).name}")

    def optimize_batch(self, resize_options: dict, quality: int, output_format: str, source_mode: str = "files"):
        if source_mode == "folder":
            input_dir = filedialog.askdirectory(title="Escolha a pasta com imagens")
            if not input_dir:
                return
            files = self._image_files_from_folder(input_dir)
            if not files:
                messagebox.showwarning("Aviso", "Nenhuma imagem suportada foi encontrada na pasta.")
                return
        else:
            files = filedialog.askopenfilenames(
                filetypes=[
                    ("Imagens", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.svg"),
                    ("Todos os arquivos", "*.*"),
                ]
            )
            if not files:
                return

        output_dir = filedialog.askdirectory(title="Escolha a pasta de saida")
        if not output_dir:
            return

        created = []
        errors = []
        original_bytes = 0
        optimized_bytes = 0

        for file_path in files:
            try:
                file_path = Path(file_path)
                original_bytes += file_path.stat().st_size
                output_path = self.service.optimize_image(file_path, output_dir, resize_options, quality, output_format)
                optimized_bytes += output_path.stat().st_size
                created.append(output_path)
            except Exception as exc:
                errors.append(f"{Path(file_path).name}: {exc}")

        if errors:
            messagebox.showwarning("Concluido com avisos", "\n".join(errors[:6]))

        summary = self._optimization_summary(len(created), original_bytes, optimized_bytes, output_dir)
        self.view.set_status(summary)
        self.view.set_optimization_summary(summary)
        self.view.last_output_dir = str(output_dir)

    def select_optimization_sources(self, source_mode: str = "files"):
        if source_mode == "folder":
            input_dir = filedialog.askdirectory(title="Escolha a pasta com imagens")
            if not input_dir:
                return
            files = self._image_files_from_folder(input_dir)
            if not files:
                messagebox.showwarning("Aviso", "Nenhuma imagem suportada foi encontrada na pasta.")
                return
        else:
            files = filedialog.askopenfilenames(
                filetypes=[
                    ("Imagens", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.svg"),
                    ("Todos os arquivos", "*.*"),
                ]
            )
            if not files:
                return

        files = [Path(path) for path in files]
        self.view.set_optimization_files(files)
        self.view.set_default_output_dir(files)
        self.view.set_status(f"{len(files)} imagem(ns) carregada(s) para otimizar.")

    def optimize_selected_files(self, files, resize_options: dict, quality: int, output_format: str, output_dir: str | Path):
        if not files:
            messagebox.showwarning("Aviso", "Marque pelo menos uma imagem para otimizar.")
            return
        if not output_dir:
            messagebox.showwarning("Aviso", "Escolha uma pasta de saida antes de otimizar.")
            return

        created = []
        errors = []
        original_bytes = 0
        optimized_bytes = 0

        for file_path in files:
            try:
                file_path = Path(file_path)
                original_bytes += file_path.stat().st_size
                output_path = self.service.optimize_image(file_path, output_dir, resize_options, quality, output_format)
                optimized_bytes += output_path.stat().st_size
                created.append(output_path)
            except Exception as exc:
                errors.append(f"{Path(file_path).name}: {exc}")

        if errors:
            messagebox.showwarning("Concluido com avisos", "\n".join(errors[:6]))

        summary = self._optimization_summary(len(created), original_bytes, optimized_bytes, output_dir)
        self.view.set_status(summary)
        self.view.set_optimization_summary(summary)
        self.view.last_output_dir = str(output_dir)

    def _image_files_from_folder(self, folder: str | Path):
        folder = Path(folder)
        return [
            path
            for path in folder.rglob("*")
            if path.is_file() and path.suffix.lower() in self.service.supported_input
        ]

    def _format_bytes(self, size: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
            value /= 1024
        return f"{size} B"

    def _optimization_summary(self, count: int, before: int, after: int, output_dir: str | Path) -> str:
        if before > 0:
            reduction = max(0, 100 - ((after / before) * 100))
            size_text = f"{self._format_bytes(before)} -> {self._format_bytes(after)} ({reduction:.1f}% menor)"
        else:
            size_text = f"0 B -> {self._format_bytes(after)}"
        return f"Otimizadas: {count} imagem(ns) | {size_text} | Saida: {output_dir}"

    def open_output_folder(self, output_dir: str | None):
        if output_dir:
            try:
                os.startfile(output_dir)
            except Exception as exc:
                messagebox.showerror("Erro", str(exc))

import os
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import numpy as np
try:
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg
except Exception:
    renderPM = None
    svg2rlg = None

@dataclass
class ImageDocument:
    path: Path | None = None
    original: Image.Image | None = None
    result: Image.Image | None = None
    dominant_colors: list[str] | None = None

class ImageService:
    supported_input = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg")

    def load_image(self, path: str | Path) -> Image.Image:
        path = Path(path)
        if path.suffix.lower() == ".svg":
            if not svg2rlg or not renderPM:
                raise RuntimeError("Para abrir SVG, instale svglib e reportlab.")
            drawing = svg2rlg(str(path))
            return renderPM.drawToPIL(drawing).convert("RGBA")
        return Image.open(path).convert("RGBA")

    def resize_for_preview(self, image: Image.Image, max_size: int = 430) -> Image.Image:
        preview = image.copy()
        preview.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return preview

    def rgb_to_hex(self, rgb) -> str:
        return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

    def hex_to_rgb(self, color: str) -> tuple[int, int, int]:
        color = color.strip().lstrip("#")
        if len(color) == 3:
            color = "".join(ch * 2 for ch in color)
        if len(color) != 6:
            raise ValueError("Use uma cor no formato #RRGGBB.")
        return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))

    def is_hex(self, color: str) -> bool:
        try:
            self.hex_to_rgb(color)
            return color.strip().startswith("#")
        except Exception:
            return False

    def dominant_colors(self, image: Image.Image, limit: int = 8) -> list[str]:
        reduced = image.copy().convert("P", palette=Image.Palette.ADAPTIVE, colors=limit).convert("RGBA")
        colors = reduced.getcolors(maxcolors=1000) or []
        colors = [item for item in colors if item[1][3] > 0]
        colors.sort(key=lambda item: item[0], reverse=True)
        return [self.rgb_to_hex(rgba[:3]) for _, rgba in colors[:limit]]

    def replace_color(
        self,
        image: Image.Image,
        old_hex: str,
        new_hex: str,
        tolerance: int,
    ) -> Image.Image:
        old_rgb = self.hex_to_rgb(old_hex)
        new_rgb = self.hex_to_rgb(new_hex)

        data = np.array(image.convert("RGBA"))
        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
        diff = (
            np.abs(r.astype(int) - old_rgb[0])
            + np.abs(g.astype(int) - old_rgb[1])
            + np.abs(b.astype(int) - old_rgb[2])
        )
        mask = (diff <= int(tolerance)) & (a > 0)
        data[:, :, 0][mask] = new_rgb[0]
        data[:, :, 1][mask] = new_rgb[1]
        data[:, :, 2][mask] = new_rgb[2]
        return Image.fromarray(data)

    def convert_image(self, image: Image.Image, output_path: str | Path, fmt: str, quality: int = 90) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = fmt.upper()
        save_image = image
        params = {}

        if fmt in {"JPEG", "JPG"}:
            fmt = "JPEG"
            save_image = self._flatten_alpha(image, "#FFFFFF")
            params["quality"] = int(quality)
            params["optimize"] = True
        elif fmt == "WEBP":
            params["quality"] = int(quality)
            params["method"] = 6
        elif fmt == "PNG":
            params["optimize"] = True

        save_image.save(output_path, format=fmt, **params)

    def optimize_image(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        resize_options: dict,
        quality: int,
        output_format: str,
    ) -> Path:
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        image = self.load_image(input_path)
        image = self.resize_by_options(image, resize_options)

        fmt = output_format.upper()
        ext = ".jpg" if fmt in {"JPG", "JPEG"} else f".{fmt.lower()}"
        output_path = output_dir / f"{input_path.stem}-otimizado{ext}"
        self.convert_image(image, output_path, fmt, quality)
        return output_path

    def resize_by_options(self, image: Image.Image, options: dict) -> Image.Image:
        mode = options.get("mode", "Largura maxima")
        width, height = image.size

        if mode == "Largura maxima":
            max_width = int(options.get("max_width") or 0)
            if max_width > 0 and width > max_width:
                ratio = max_width / width
                return image.resize((max_width, max(1, int(height * ratio))), Image.Resampling.LANCZOS)

        elif mode == "Altura maxima":
            max_height = int(options.get("max_height") or 0)
            if max_height > 0 and height > max_height:
                ratio = max_height / height
                return image.resize((max(1, int(width * ratio)), max_height), Image.Resampling.LANCZOS)

        elif mode == "Porcentagem":
            percent = int(options.get("percent") or 100)
            percent = max(1, min(percent, 100))
            if percent < 100:
                ratio = percent / 100
                return image.resize((max(1, int(width * ratio)), max(1, int(height * ratio))), Image.Resampling.LANCZOS)

        elif mode == "Maximo de pixels":
            max_pixels = int(options.get("max_pixels") or 0)
            current_pixels = width * height
            if max_pixels > 0 and current_pixels > max_pixels:
                ratio = (max_pixels / current_pixels) ** 0.5
                return image.resize((max(1, int(width * ratio)), max(1, int(height * ratio))), Image.Resampling.LANCZOS)

        elif mode == "Tamanho exato":
            target_width = int(options.get("target_width") or 0)
            target_height = int(options.get("target_height") or 0)
            keep_ratio = bool(options.get("keep_ratio", True))
            if target_width > 0 and target_height > 0:
                if keep_ratio:
                    copy = image.copy()
                    copy.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    return copy
                return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return image

    def _flatten_alpha(self, image: Image.Image, background: str) -> Image.Image:
        if image.mode not in ("RGBA", "LA"):
            return image.convert("RGB")
        bg = Image.new("RGB", image.size, background)
        bg.paste(image, mask=image.getchannel("A"))
        return bg
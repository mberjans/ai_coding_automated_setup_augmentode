# Registry mapping from detected format keys to parser callables
# Functional style, no OOP or regex

from .parsers import txt_md
from .parsers import docx_pptx
from .parsers import tabular
from .parsers import pdf as pdf_mod
from .parsers import image_svg


_REGISTRY = {
    "txt": txt_md.parse_txt,
    "md": txt_md.parse_md,
    "docx": docx_pptx.parse_docx,
    "pptx": docx_pptx.parse_pptx,
    "xlsx": tabular.parse_xlsx,
    "csv": tabular.parse_csv,
    "tsv": tabular.parse_tsv,
    "pdf": pdf_mod.parse_pdf,
    "png": image_svg.parse_image,
    "jpeg": image_svg.parse_image,
    "svg": image_svg.parse_svg,
}


def get_registry():
    return _REGISTRY


def resolve(fmt):
    if fmt in _REGISTRY:
        return _REGISTRY[fmt]
    return None

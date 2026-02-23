# pdf_merge.py

A small command-line script that merges PDF and image files (JPG/JPEG/PNG) into a single PDF.

- Supports input files in any order and merges them in that order.
- Images are converted to PDF pages using Pillow.
- Scaling options let you preserve original image size, fit to common paper sizes, or match the width of the widest PDF page.

See the script at [pdf_merge.py](pdf_merge.py).

**Quick Start (for non-coders)**

- Requirements: Python 3.8+ and internet access to install packages.
- Install dependencies (run in PowerShell or CMD):

```powershell
python -m pip install --user pypdf Pillow
```

- Put the files you want to merge in the same folder as `pdf_merge.py` (or use full paths).
- Open PowerShell, change to the folder and run an example:

```powershell
cd "C:\Docs\Family\Tim\Code\python\pdf_merger"
python pdf_merge.py --files ".\image.jpeg" ".\document.pdf" --output "merged.pdf" --scale auto-width
```

Arguments:
- `--files` accepts one or more files (PDF, JPG, JPEG, PNG) separated by spaces. Use quotes if filenames contain spaces.
- `--output` must be the desired PDF filename. If you omit the `.pdf` extension the script will add it automatically.
- `--scale` controls how images are scaled (see below). The option is case-insensitive (e.g. `a4` and `A4` both work).

**Common `--scale` options**
- `original` (default): keep the image's original pixel dimensions.
- `auto-width` : scale images so their page width matches the widest PDF page found among the inputs (preserves aspect ratio). Does not scale PDF pages.
- `letter`, `legal`, `a4`, `a3`: scale images to fit the chosen paper size (sizes expressed in PDF points; images centered on that page).

Example (A4):

```powershell
python pdf_merge.py --files image1.jpg image2.png document.pdf --output output_a4.pdf --scale a4
```

**Troubleshooting (quick)**
- "Error: Input file not found": check the path and filename, and use quotes if there are spaces.
- "Error: Unsupported file format": only PDF, JPG, JPEG and PNG are supported by default.
- If pages look unexpectedly small/wide: ensure you are using `--scale original` (no scaling) or `--scale auto-width` if you want images matched to PDFs.

---

**Implementation details (for developers)**

Overview
- The script uses `pypdf` for reading and writing PDFs and `Pillow` (`PIL`) for image processing.
- Images are converted to PDF pages and appended to an output `PdfWriter` in the same order provided on the command line.

Key points in the code (see `pdf_merge.py`):
- `PAPER_SIZES` contains paper sizes in PDF points (1 point = 1/72 inch). Use these to center/fit images.
- `--scale` is normalized to lowercase to make it case-insensitive. Valid keys are the keys of `PAPER_SIZES` plus `auto-width`.
- `auto-width` behavior: the script reads all PDF inputs using `PdfReader`, inspects each page's `mediabox.width` (in points), and finds the widest page width. Images are resized so their width (in points) matches that value; height is adjusted to preserve aspect ratio.
- Image-to-PDF mapping: the script saves intermediate image canvases as temporary single-page PDFs using `canvas.save(..., 'PDF', resolution=72.0)`. Using 72 DPI makes image pixels map 1:1 to PDF points (1 px == 1 point), which keeps sizes predictable.
- For scaled-to-paper options (e.g., `A4`), the script uses `img.thumbnail(paper_size, Image.Resampling.LANCZOS)` then centers the image on a white canvas the size of the target paper.
- Temporary files: images are saved as temporary `*.pdf` next to the source and removed after appending. This is simple and reliable but can be replaced with an in-memory approach if desired.

Dependencies
- pypdf (reading/writing PDFs)
- Pillow (image processing)

Testing
- Try mixing several PDFs with various page sizes and a couple of images. Test `--scale auto-width` to confirm image widths match the largest PDF page width.

Extensions and suggestions
- Use `io.BytesIO` instead of temporary files to avoid touching disk when converting images to PDFs.
- Add support for TIFF or other image types by including them in the allowed extensions and verifying Pillow can open them.
- Add an option to preserve EXIF orientation explicitly (Pillow usually handles rotation on open, but you can add extra steps if needed).
- Replace temporary filenames with `tempfile.NamedTemporaryFile(delete=False)` if you want safer temporary file handling.

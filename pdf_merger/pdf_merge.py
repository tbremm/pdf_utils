from pypdf import PdfWriter, PdfReader
from PIL import Image
import argparse
import os

# Define paper sizes in points (1 point = 1/72 inch)
PAPER_SIZES = {
    "original": None,           # Preserve original scale
    "auto-width": "auto-width", # Scale to match the width of the widest PDF
    "letter": (612, 792),       # 8.5 x 11 inches
    "legal": (612, 1008),       # 8.5 x 14 inches
    "a4": (595, 842),           # 210 x 297 mm
    "a3": (842, 1191)           # 297 x 420 mm
}

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('--files', type=str, nargs='+', help='One or more input files (PDF, JPG, JPEG, PNG)')
    argparser.add_argument('--output', required=True, type=str, help="Output file name")
    argparser.add_argument('--scale', type=str, default="original",
                           help="Scaling option for images (case-insensitive). Supported options: original (no scaling), auto-width (scale image widths to match the widest PDF), letter (8.5x11 in), legal (8.5x14 in), a4 (210x297 mm), a3 (297x420 mm)")
    args = argparser.parse_args()

    # Validate input files
    if not args.files:
        print("Error: No input files provided. Use --files to specify one or more files.")
        exit(1)

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: Input file not found: {file_path}")
            exit(1)
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
            print(f"Error: Unsupported file format '{file_ext}' for file: {file_path}")
            print("Supported formats: PDF, JPG, JPEG, PNG")
            exit(1)

    # Validate output filename
    output_filename = args.output
    if not output_filename.lower().endswith('.pdf'):
        print(f"Warning: Output filename '{output_filename}' does not have a .pdf extension. Adding it.")
        output_filename += '.pdf'

    # Validate and normalize scale option (case-insensitive)
    scale = args.scale.lower()
    if scale not in PAPER_SIZES:
        print(f"Error: Invalid scale option '{args.scale}'")
        print(f"Supported options (case-insensitive): {', '.join(PAPER_SIZES.keys())}")
        exit(1)

    paper_size = PAPER_SIZES[scale]
    merger = PdfWriter()

    # Determine the width of the widest PDF if 'auto-width' scaling is selected
    widest_width = None
    if scale == "auto-width":
        for file_path in args.files:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".pdf":
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        width = float(page.mediabox.width)
                        if widest_width is None or width > widest_width:
                            widest_width = width
                except Exception as e:
                    print(f"Warning: Could not read PDF file '{file_path}': {e}")
        if widest_width is None:
            print("No PDF files found to determine the widest width. Defaulting to original scale.")
            scale = "original"

    for file_path in args.files:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext in ['.pdf']:
            # Append PDF files directly
            try:
                merger.append(file_path)
            except Exception as e:
                print(f"Error: Could not append PDF file '{file_path}': {e}")
                exit(1)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            # Convert image files to PDF and append
            try:
                with Image.open(file_path) as img:
                    # Ensure image is in RGB mode
                    if img.mode in ("RGBA", "P"):  # Convert if necessary
                        img = img.convert("RGB")

                    if scale == "original":
                        # Preserve original scale
                        canvas = img
                    elif scale == "auto-width" and widest_width is not None:
                        # Scale image to match the width of the widest PDF
                        aspect_ratio = img.height / img.width
                        new_width = int(widest_width)
                        new_height = int(new_width * aspect_ratio)

                        # Resize the image to the new dimensions
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # Create a blank canvas with the new dimensions
                        canvas = Image.new("RGB", (new_width, new_height), "white")
                        canvas.paste(img, (0, 0))
                    else:
                        # Scale image to fit the paper size while maintaining aspect ratio
                        img.thumbnail(paper_size, Image.Resampling.LANCZOS)

                        # Create a blank canvas with the paper size
                        canvas = Image.new("RGB", paper_size, "white")

                        # Center the image on the canvas
                        x_offset = (paper_size[0] - img.width) // 2
                        y_offset = (paper_size[1] - img.height) // 2
                        canvas.paste(img, (x_offset, y_offset))

                    # Save the canvas as a temporary PDF and append
                    temp_pdf_path = file_path + ".pdf"
                    canvas.save(temp_pdf_path, "PDF", resolution=72.0)
                    merger.append(temp_pdf_path)
                    # Remove the temporary PDF after appending
                    os.remove(temp_pdf_path)
            except Exception as e:
                print(f"Error: Could not process image file '{file_path}': {e}")
                exit(1)

    # Write the merged PDF
    try:
        merger.write(output_filename)
        merger.close()
        print(f"Successfully created: {output_filename}")
    except Exception as e:
        print(f"Error: Could not write output file '{output_filename}': {e}")
        exit(1)
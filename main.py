from pathlib import Path

from PIL import ImageOps
from pymupdf import Rect, paper_size, open, pymupdf, Page, Point, get_text_length

from drawing import draw_mark
from tiling import cover_with_tiles

A4 = Point(paper_size('A4'))
A4_L = Point(paper_size('A4-l'))
CM = 72 / 2.54

# configuration:
SAMPLE_PDF_PATH = Path("C:\\Users\\Szymon\\Downloads\\Drawing 1-5.pdf")
OUTPUT_PDF_PATH = Path('tiled.pdf')
STROKE_OPACITY = 0.2
MARK_SIZE = 1 * CM
MARK_POSITIONS = (0.1, 0.9)
PAGE = A4_L
MARGIN = 0.4 * CM
FONTSIZE = 100
DPI = 300

TILE = Point(PAGE.x - 2 * MARGIN, PAGE.y - 2 * MARGIN)

def get_roi_rect(page: Page) -> Rect:
    image = page.get_pixmap(dpi=DPI).pil_image()
    return Rect(ImageOps.invert(image).getbbox()) / DPI * 72

def main():
    input_pdf = open(SAMPLE_PDF_PATH)
    if input_pdf.page_count != 1:
        raise ValueError('Input PDF file is not a single page')
    input_page = input_pdf.load_page(0)

    roi = get_roi_rect(input_page)

    # input_page.draw_rect(roi, dashes="[5] 0", color=(1, 0, 0))

    output_pdf = pymupdf.open()

    for i, input_page_rect in enumerate(cover_with_tiles(roi, TILE)):
        # input_page.draw_rect(input_page_rect, dashes="[1] 0", color=(0, 1, 0))
        input_page_rect_clipped = input_page_rect & input_page.rect

        output_page_rect = input_page_rect_clipped - (input_page_rect.x0, input_page_rect.y0,input_page_rect.x0, input_page_rect.y0)
        output_page_rect = output_page_rect + ((PAGE.x - TILE.x) / 2,(PAGE.y - TILE.y) / 2, (PAGE.x - TILE.x) / 2,(PAGE.y - TILE.y) / 2)

        output_page = output_pdf.new_page(width=PAGE.x, height=PAGE.y)
        output_page.show_pdf_page(output_page_rect, input_pdf, clip=input_page_rect)

        outline_rect = Rect(
            (PAGE.x - TILE.x) / 2, (PAGE.y - TILE.y) / 2,
            (PAGE.x - TILE.x) / 2 + TILE.x, (PAGE.y - TILE.y) / 2 + TILE.y)
        output_page.draw_rect(outline_rect, dashes="[5] 0", stroke_opacity=STROKE_OPACITY)

        for mark_dist in MARK_POSITIONS:
            points = [
                Point(outline_rect.x0, outline_rect.y0 + outline_rect.height * mark_dist),
                Point(outline_rect.x1, outline_rect.y0 + outline_rect.height * mark_dist),
                Point(outline_rect.x0 + outline_rect.width * mark_dist, outline_rect.y0),
                Point(outline_rect.x0 + outline_rect.width * mark_dist, outline_rect.y1),
            ]
            for point in points:
                draw_mark(output_page, point, MARK_SIZE, stroke_opacity=STROKE_OPACITY)

        title = f"{i + 1}"
        title_width = get_text_length(title, fontsize=FONTSIZE)

        title_pos = Point((PAGE.x - title_width) / 2, (PAGE.y + FONTSIZE * 0.7) / 2)
        output_page.insert_text(title_pos, title, fontsize=FONTSIZE, fill_opacity=0.05, lineheight=1)
    output_pdf.save(OUTPUT_PDF_PATH)
    input_pdf.save("annotated.pdf")


if __name__ == '__main__':
    main()

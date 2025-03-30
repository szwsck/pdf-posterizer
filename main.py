from pathlib import Path
from typing import Generator

from PIL import ImageOps
from pymupdf import Rect, paper_size, open, pymupdf, Page, Point, get_text_length

SAMPLE_PDF_PATH = Path('/Users/szymon.wysocki/Downloads/torbadama_pieces.pdf')
OUTPUT_PDF_PATH = Path('/Users/szymon.wysocki/PycharmProjects/pdf-cutter/tiled.pdf')

DPI = 300

A4 = Point(paper_size('A4-l'))
CM = 72 / 2.54
TILE = Point(A4.x - 2 * CM, A4.y - 2 * CM)

STROKE_OPACITY = 0.2
MARK_SIZE = CM
MARK_POSITIONS = (0.1, 0.9)

FONTSIZE = 100


def get_roi_rect(page: Page) -> Rect:
    image = page.get_pixmap(dpi=DPI).pil_image()
    return Rect(ImageOps.invert(image).getbbox()) / DPI * 72


def get_tiles(region: Rect, tile_size: Point) -> Generator[Rect, None, None]:
    y = region.y0
    while y < region.y1:
        x = region.x0
        while x < region.x1:
            yield Rect(x, y, x + tile_size.x, y + tile_size.y)
            x += tile_size.x
        y += tile_size.y


def draw_mark(page: Page, pos: Point):
    bbox = Rect(pos - 0.5 * MARK_SIZE, pos + 0.5 * MARK_SIZE)
    page.draw_line(bbox.tl, bbox.br, stroke_opacity=STROKE_OPACITY)
    page.draw_line(bbox.bl, bbox.tr, stroke_opacity=STROKE_OPACITY)
    page.draw_line(Point(bbox.x0, pos.y), Point(bbox.x1, pos.y), stroke_opacity=STROKE_OPACITY)
    page.draw_line(Point(pos.x, bbox.y0), Point(pos.x, bbox.y1), stroke_opacity=STROKE_OPACITY)
    page.draw_circle(pos, MARK_SIZE / 2, stroke_opacity=STROKE_OPACITY)


def main():
    input_pdf = open(SAMPLE_PDF_PATH)
    if input_pdf.page_count != 1:
        raise ValueError('Input PDF file is not a single page')
    input_page = input_pdf.load_page(0)

    roi = get_roi_rect(input_page)

    output_pdf = pymupdf.open()

    for i, input_page_rect in enumerate(get_tiles(roi, TILE)):
        input_page_rect_clipped = input_page_rect & input_page.rect

        output_page_rect = Rect(
            input_page_rect_clipped.x0 - input_page_rect.x0 + (A4.x - TILE.x) / 2,
            input_page_rect_clipped.y0 - input_page_rect.y0 + (A4.y - TILE.y) / 2,
            input_page_rect_clipped.x1 - input_page_rect.x0 + (A4.x - TILE.x) / 2,
            input_page_rect_clipped.y1 - input_page_rect.y0 + (A4.y - TILE.y) / 2
        )

        output_page = output_pdf.new_page(width=A4.x, height=A4.y)
        output_page.show_pdf_page(output_page_rect, input_pdf, clip=input_page_rect)

        outline_rect = Rect(
            (A4.x - TILE.x) / 2, (A4.y - TILE.y) / 2,
            (A4.x - TILE.x) / 2 + TILE.x, (A4.y - TILE.y) / 2 + TILE.y)
        output_page.draw_rect(outline_rect, dashes="[5] 0", stroke_opacity=STROKE_OPACITY)

        for mark_dist in MARK_POSITIONS:
            points = [
                Point(outline_rect.x0, outline_rect.y0 + outline_rect.height * mark_dist),
                Point(outline_rect.x1, outline_rect.y0 + outline_rect.height * mark_dist),
                Point(outline_rect.x0 + outline_rect.width * mark_dist, outline_rect.y0),
                Point(outline_rect.x0 + outline_rect.width * mark_dist, outline_rect.y1),
            ]
            for point in points:
                draw_mark(output_page, point)

        title = f"{i + 1}"
        title_width = get_text_length(title, fontsize=FONTSIZE)

        title_pos = Point((A4.x - title_width) / 2, (A4.y + FONTSIZE*0.7) / 2)
        output_page.insert_text(title_pos, title, fontsize=FONTSIZE, fill_opacity=0.05, lineheight=1)
    output_pdf.save(OUTPUT_PDF_PATH)


if __name__ == '__main__':
    main()

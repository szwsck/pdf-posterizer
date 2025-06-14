from pymupdf import Rect, Page, Point


def draw_mark(page: Page, pos: Point, size: float, **kwargs):
    bbox = Rect(pos - 0.5 * size, pos + 0.5 * size)
    page.draw_line(bbox.tl, bbox.br, **kwargs)
    page.draw_line(bbox.bl, bbox.tr, **kwargs)
    page.draw_line(Point(bbox.x0, pos.y), Point(bbox.x1, pos.y), **kwargs)
    page.draw_line(Point(pos.x, bbox.y0), Point(pos.x, bbox.y1), **kwargs)
    page.draw_circle(pos, size / 2, **kwargs)

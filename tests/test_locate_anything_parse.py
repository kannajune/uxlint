"""Test LocateAnything's box-token parser without loading the model.

`_parse_boxes` is a pure staticmethod; importing it does not pull in torch.
"""

from uxlens.locator.locate_anything import LocateAnythingLocator

parse = LocateAnythingLocator._parse_boxes


def test_parses_box_to_pixels():
    # 0..1000 normalized -> pixels on a 1000x1000 image is identity.
    boxes = parse("<box>100 200 300 400</box>", "cta", (1000, 1000))
    assert len(boxes) == 1
    b = boxes[0]
    assert (b.x1, b.y1, b.x2, b.y2) == (100, 200, 300, 400)
    assert b.label == "cta"


def test_scales_to_image_size():
    boxes = parse("<box>0 0 500 1000</box>", "x", (200, 800))
    b = boxes[0]
    assert (b.x1, b.y1, b.x2, b.y2) == (0, 0, 100, 800)


def test_multiple_boxes():
    text = "stuff <box>0 0 10 10</box> and <box>20 20 30 30</box>"
    assert len(parse(text, "x", (1000, 1000))) == 2


def test_point_becomes_small_box():
    boxes = parse("<box>500 500</box>", "p", (1000, 1000))
    assert len(boxes) == 1
    b = boxes[0]
    assert b.width == 10 and b.height == 10


def test_no_boxes():
    assert parse("no coordinates here", "x", (100, 100)) == []

"""Targeted unit tests for map callout layout and collision avoidance solver."""

from src.services.map_callout_layout import (
    filter_valid_tour_stops,
    format_dual_distance,
    solve_callout_positions,
    solve_transit_badge_position,
    box_intersects_circle,
    boxes_intersect,
    segment_intersects_box,
)


def test_format_dual_distance():
    assert format_dual_distance("2.5 km") == "2.5 km (1.6 mi)"
    assert format_dual_distance("3.0 mi") == "3.0 mi"
    assert format_dual_distance(None) == "1.5 km (0.9 mi)"


def test_filter_valid_tour_stops():
    stops = [
        {"name": "Overview", "is_itinerary_overview": True, "coords": (46.2, 6.1)},
        {"name": "Stop 1", "coords": (46.207, 6.155)},
        {"name": "Stop 2", "coords": (46.204, 6.151)},
    ]
    coords, valid = filter_valid_tour_stops(stops)
    assert len(coords) == 2
    assert len(valid) == 2
    assert valid[0]["name"] == "Stop 1"
    assert valid[1]["name"] == "Stop 2"


def test_solve_callout_positions_no_overlap():
    pts = [(2070, 1236), (2013, 1308), (1941, 1392), (1893, 1410), (1797, 750), (1770, 849)]
    route_segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    pin_r = 28
    card_sizes = [(260, 50) for _ in pts]
    hud = (100, 80, 1140, 320)

    placements = solve_callout_positions(pts, pin_r, card_sizes, route_segs, hud)
    assert len(placements) == len(pts)

    boxes = [p[0] for p in placements]
    for i, b1 in enumerate(boxes):
        # Must not overlap other boxes
        for j, b2 in enumerate(boxes):
            if i != j:
                assert not boxes_intersect(b1, b2, margin=5)
        # Must not overlap pins
        for pt in pts:
            assert not box_intersects_circle(b1, pt, pin_r + 10)
        # Must not intersect route segments
        for pa, pb in route_segs:
            assert not segment_intersects_box(pa, pb, b1, buffer=10)


def test_solve_transit_badge_position_perpendicular():
    p1 = (1000, 1000)
    p2 = (1500, 1000)
    route_segs = [(p1, p2)]
    pin_r = 28
    pixel_pts = [p1, p2]
    placed_boxes = []
    hud = (100, 80, 500, 300)

    badge = solve_transit_badge_position(
        p1, p2, 200, 40, route_segs, pin_r, pixel_pts, placed_boxes, hud
    )
    assert badge is not None
    # Verify badge does not intersect the route segment
    assert not segment_intersects_box(p1, p2, badge, buffer=10)

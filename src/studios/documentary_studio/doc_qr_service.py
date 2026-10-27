"""Broadcast-grade 4K Scan-and-Go Itinerary QR Code Overlay Service.

Renders cinema-grade frosted-glass QR cards for tourist itineraries and city tours,
enabling viewers to instantly scan and load official turn-by-turn Google Maps routes on phone.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_overlay_service import _load_font


def generate_qr_matrix(url: str, box_size: int = 240) -> np.ndarray:
    """Encodes URL to high-contrast scannable QR module image via OpenCV."""
    clean_url = (url or "https://maps.google.com").strip()
    try:
        enc = cv2.QRCodeEncoder.create()
        raw = enc.encode(clean_url)
        if raw is not None and raw.ndim == 2:
            # Add standard 4-module quiet zone border for reliable phone scanning
            padded = cv2.copyMakeBorder(raw, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=255)
            # Scale to crisp high-resolution box with nearest neighbor
            scaled = cv2.resize(padded, (box_size, box_size), interpolation=cv2.INTER_NEAREST)
            # Invert: OpenCV encoder outputs 0 for dark and 255 for white
            return scaled
    except Exception as ex:
        logger.warning(f"cv2_qr_encoder_failed: {ex}")

    # Fallback high-contrast test matrix
    dummy = np.full((box_size, box_size), 255, dtype=np.uint8)
    cv2.rectangle(dummy, (20, 20), (box_size - 20, box_size - 20), 0, 8)
    cv2.rectangle(dummy, (50, 50), (box_size - 50, box_size - 50), 0, -1)
    return dummy


def create_itinerary_qr_overlay(
    route_url: str,
    destination_name: Optional[str] = None,
    target_res: Tuple[int, int] = (3840, 2160),
) -> np.ndarray:
    """Renders a prestigious 4K RGBA frosted-glass QR card in the bottom-right safe quadrant."""
    w, h = target_res
    s = h / 2160.0

    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_badge = _load_font(int(20 * s), bold=True)
    font_title = _load_font(int(32 * s), bold=True)
    font_sub = _load_font(int(22 * s), bold=False)
    font_hint = _load_font(int(19 * s), bold=False)

    dest_disp = (destination_name or "Official Tour Itinerary").strip()[:42]

    qr_dim = int(220 * s)
    qr_img = generate_qr_matrix(route_url, box_size=qr_dim)

    card_w = int(760 * s)
    card_h = int(260 * s)

    # YouTube 16:9 End-Screen Safe Zone:
    # YouTube places recommendation cards in top-left (0-65% width) and top-right (subscribe).
    # This card is locked in bottom-right safe quadrant (74-94% width, 73-85% height), 100% unobstructed.
    card_x = int(w * 0.94) - card_w
    card_y = int(h * 0.85) - card_h

    card_rgba = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    card_rgba[:, :] = [12, 16, 26, 225]  # Deep frosted obsidian

    # Golden top accent bar & subtle glass borders
    bar_h = max(3, int(4 * s))
    card_rgba[:bar_h, :] = [255, 204, 51, 255]
    card_rgba[-1, :] = [255, 255, 255, 50]
    card_rgba[:, 0] = [255, 255, 255, 50]
    card_rgba[:, -1] = [255, 255, 255, 50]

    overlay[card_y : card_y + card_h, card_x : card_x + card_w] = card_rgba
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    # 1. Left: White QR Module Badge with crisp borders
    qr_pad = int(18 * s)
    qr_x = card_x + qr_pad
    qr_y = card_y + int(24 * s)

    # Paste QR code as RGBA into image
    qr_rgba = np.zeros((qr_dim, qr_dim, 4), dtype=np.uint8)
    qr_rgba[:, :, 0] = qr_img
    qr_rgba[:, :, 1] = qr_img
    qr_rgba[:, :, 2] = qr_img
    qr_rgba[:, :, 3] = 255

    pil_qr = Image.fromarray(qr_rgba)
    pil_overlay.paste(pil_qr, (qr_x, qr_y))

    # Re-wrap draw context
    draw = ImageDraw.Draw(pil_overlay)
    # Subtle frame around QR
    draw.rectangle(
        [(qr_x - 2, qr_y - 2), (qr_x + qr_dim + 2, qr_y + qr_dim + 2)],
        outline=(255, 215, 0, 160),
        width=max(1, int(2 * s)),
    )

    # 2. Right: Text details
    cur_x = qr_x + qr_dim + int(24 * s)
    cur_y = card_y + int(28 * s)

    draw.text((cur_x, cur_y), "📱 SCAN FOR GOOGLE MAPS ROUTE", fill=(255, 215, 0, 240), font=font_badge)
    cur_y += int(30 * s)

    draw.text((cur_x, cur_y), dest_disp, fill=(255, 255, 255, 255), font=font_title)
    cur_y += int(46 * s)

    draw.text((cur_x, cur_y), "📍 Turn-by-Turn GPS Walking & Transit Guide", fill=(220, 235, 255, 220), font=font_sub)
    cur_y += int(38 * s)

    # Divider hairline
    div_w = int(card_w - (cur_x - card_x) - int(24 * s))
    draw.line([(cur_x, cur_y), (cur_x + div_w, cur_y)], fill=(255, 215, 0, 60), width=1)
    cur_y += int(12 * s)

    draw.text((cur_x, cur_y), "👉 Open phone camera & tap banner to launch", fill=(240, 225, 185, 220), font=font_hint)

    return np.array(pil_overlay)


__all__ = [
    "generate_qr_matrix",
    "create_itinerary_qr_overlay",
]

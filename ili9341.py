"""
ILI9341 SPI TFT LCD Driver for MicroPython (ESP32 / Wokwi)
Optimized for high-speed dashboard graphics on 320x240 color screens.
"""

import time
import struct

try:
    from micropython import const
except ImportError:
    const = lambda x: x

# ILI9341 Commands
SWRESET = const(0x01)
SLPOUT = const(0x11)
DISPON = const(0x29)
CASET = const(0x2A)
PASET = const(0x2B)
RAMWR = const(0x2C)
MADCTL = const(0x36)
COLMOD = const(0x3A)


def color565(r, g, b):
    """Convert RGB888 (0-255) to 16-bit RGB565 format."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


# Standard 8x8 ASCII font (compact subset: space through '~')
# 5x7 characters padded to 8x8
FONT_8X8 = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    '!': [0x00, 0x00, 0x5F, 0x00, 0x00],
    '"': [0x00, 0x07, 0x00, 0x07, 0x00],
    '#': [0x14, 0x7F, 0x14, 0x7F, 0x14],
    '$': [0x24, 0x2A, 0x7F, 0x2A, 0x12],
    '%': [0x23, 0x13, 0x08, 0x64, 0x62],
    '&': [0x36, 0x49, 0x55, 0x22, 0x50],
    "'": [0x00, 0x05, 0x03, 0x00, 0x00],
    '(': [0x00, 0x1C, 0x22, 0x41, 0x00],
    ')': [0x00, 0x41, 0x22, 0x1C, 0x00],
    '*': [0x08, 0x2A, 0x1C, 0x2A, 0x08],
    '+': [0x08, 0x08, 0x3E, 0x08, 0x08],
    ',': [0x00, 0x50, 0x30, 0x00, 0x00],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '.': [0x00, 0x60, 0x60, 0x00, 0x00],
    '/': [0x20, 0x10, 0x08, 0x04, 0x02],
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
    '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
    '2': [0x42, 0x61, 0x51, 0x49, 0x46],
    '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
    ':': [0x00, 0x36, 0x36, 0x00, 0x00],
    ';': [0x00, 0x56, 0x36, 0x00, 0x00],
    '<': [0x08, 0x14, 0x22, 0x41, 0x00],
    '=': [0x14, 0x14, 0x14, 0x14, 0x14],
    '>': [0x00, 0x41, 0x22, 0x14, 0x08],
    '?': [0x02, 0x01, 0x51, 0x09, 0x06],
    '@': [0x32, 0x49, 0x79, 0x41, 0x3E],
    'A': [0x7E, 0x11, 0x11, 0x11, 0x7E],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
    'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
    'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
    'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
    'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'S': [0x46, 0x49, 0x49, 0x49, 0x31],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
    'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
    'W': [0x7F, 0x20, 0x18, 0x20, 0x7F],
    'X': [0x63, 0x14, 0x08, 0x14, 0x63],
    'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
    'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
    'h': [0x7F, 0x08, 0x04, 0x04, 0x78],
    'm': [0x7C, 0x04, 0x18, 0x04, 0x78],
    'p': [0x7C, 0x14, 0x14, 0x14, 0x08],
    'r': [0x7C, 0x08, 0x04, 0x04, 0x08],
}

# 7-Segment segment activation map (a, b, c, d, e, f, g)
SEGMENTS_7 = {
    '0': (1, 1, 1, 1, 1, 1, 0),
    '1': (0, 1, 1, 0, 0, 0, 0),
    '2': (1, 1, 0, 1, 1, 0, 1),
    '3': (1, 1, 1, 1, 0, 0, 1),
    '4': (0, 1, 1, 0, 0, 1, 1),
    '5': (1, 0, 1, 1, 0, 1, 1),
    '6': (1, 0, 1, 1, 1, 1, 1),
    '7': (1, 1, 1, 0, 0, 0, 0),
    '8': (1, 1, 1, 1, 1, 1, 1),
    '9': (1, 1, 1, 1, 0, 1, 1),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '-': (0, 0, 0, 0, 0, 0, 1),
}


class ILI9341:
    """MicroPython driver for ILI9341 TFT display."""

    def __init__(self, spi, cs, dc, rst=None, width=320, height=240, rotation=90):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height

        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.rst:
            self.rst.init(self.rst.OUT, value=1)

        self._init_display(rotation)

    def _write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)

    def _write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)

    def _init_display(self, rotation):
        if self.rst:
            self.rst.value(0)
            time.sleep_ms(20)
            self.rst.value(1)
            time.sleep_ms(50)

        self._write_cmd(SWRESET)
        time.sleep_ms(120)

        self._write_cmd(SLPOUT)
        time.sleep_ms(120)

        self._write_cmd(COLMOD)
        self._write_data(0x55)  # 16-bit color (RGB565)

        # Rotation: 90 = landscape, 270 = inverted landscape
        self._write_cmd(MADCTL)
        if rotation == 90:
            self._write_data(0x28 | 0x08)  # BGR bit + landscape (MY=0, MX=0, MV=1)
        elif rotation == 270:
            self._write_data(0xE8 | 0x08)
        elif rotation == 180:
            self._write_data(0x88 | 0x08)
        else:
            self._write_data(0x48 | 0x08)

        self._write_cmd(DISPON)
        time.sleep_ms(20)
        self.clear(0)

    def set_window(self, x0, y0, x1, y1):
        """Set address window for pixel writes."""
        self._write_cmd(CASET)
        self._write_data(struct.pack('>HH', x0, x1))
        self._write_cmd(PASET)
        self._write_data(struct.pack('>HH', y0, y1))
        self._write_cmd(RAMWR)

    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle with a single 16-bit color."""
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        if w <= 0 or h <= 0:
            return

        self.set_window(x, y, x + w - 1, y + h - 1)
        color_bytes = struct.pack('>H', color)
        # Send in chunks of up to 64 pixels to optimize SPI buffer usage
        chunk_pixels = min(w * h, 64)
        buf = color_bytes * chunk_pixels
        total_pixels = w * h
        self.dc.value(1)
        self.cs.value(0)
        while total_pixels > 0:
            count = min(total_pixels, chunk_pixels)
            if count == chunk_pixels:
                self.spi.write(buf)
            else:
                self.spi.write(color_bytes * count)
            total_pixels -= count
        self.cs.value(1)

    def draw_pixel(self, x, y, color):
        """Draw a single pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            self._write_data(struct.pack('>H', color))

    def draw_line(self, x0, y0, x1, y1, color):
        """Bresenham's line algorithm."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.draw_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_thick_line(self, x0, y0, x1, y1, width, color):
        """Draw a line with thickness (useful for tachometer bars)."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        half_w = width // 2
        for offset in range(-half_w, half_w + 1):
            if abs(x1 - x0) < abs(y1 - y0):
                self.draw_line(x0 + offset, y0, x1 + offset, y1, color)
            else:
                self.draw_line(x0, y0 + offset, x1, y1 + offset, color)

    def clear(self, color=0):
        """Clear entire display."""
        self.fill_rect(0, 0, self.width, self.height, color)

    def draw_char(self, x, y, char, color, bg=None, size=1):
        """Draw a single ASCII character."""
        pattern = FONT_8X8.get(char, FONT_8X8[' '])
        for col_idx, col_bits in enumerate(pattern):
            for row_idx in range(8):
                if (col_bits >> row_idx) & 1:
                    if size == 1:
                        self.draw_pixel(x + col_idx, y + row_idx, color)
                    else:
                        self.fill_rect(x + col_idx * size, y + row_idx * size, size, size, color)
                elif bg is not None:
                    if size == 1:
                        self.draw_pixel(x + col_idx, y + row_idx, bg)
                    else:
                        self.fill_rect(x + col_idx * size, y + row_idx * size, size, size, bg)

    def draw_text(self, x, y, text, color, bg=None, size=1):
        """Draw a text string using the 8x8 font."""
        cursor_x = x
        for char in text:
            self.draw_char(cursor_x, y, char, color, bg, size)
            cursor_x += (len(FONT_8X8.get(char, [0]*5)) + 1) * size

    def draw_7seg_digit(self, x, y, digit_char, color, bg, w=20, h=36, t=4):
        """
        Draw a digital 7-segment digit (authentic S2000 speedometer style).
        Segments: a=top, b=top-r, c=bot-r, d=bot, e=bot-l, f=top-l, g=mid
        """
        segs = SEGMENTS_7.get(digit_char, SEGMENTS_7[' '])
        half_h = h // 2

        # Clear background bounding box
        if bg is not None:
            self.fill_rect(x, y, w, h, bg)

        c = lambda active: color if active else (bg if bg is not None else color)
        
        # a: top horizontal
        if segs[0]:
            self.fill_rect(x + t, y, w - 2 * t, t, color)
        # b: top-right vertical
        if segs[1]:
            self.fill_rect(x + w - t, y + t, t, half_h - t, color)
        # c: bottom-right vertical
        if segs[2]:
            self.fill_rect(x + w - t, y + half_h, t, half_h - t, color)
        # d: bottom horizontal
        if segs[3]:
            self.fill_rect(x + t, y + h - t, w - 2 * t, t, color)
        # e: bottom-left vertical
        if segs[4]:
            self.fill_rect(x, y + half_h, t, half_h - t, color)
        # f: top-left vertical
        if segs[5]:
            self.fill_rect(x, y + t, t, half_h - t, color)
        # g: middle horizontal
        if segs[6]:
            self.fill_rect(x + t, y + half_h - t // 2, w - 2 * t, t, color)

    def draw_7seg_number(self, x, y, num_str, color, bg=0, w=20, h=36, t=4, gap=6):
        """Draw multiple 7-segment digits side-by-side."""
        cursor_x = x
        for char in num_str:
            self.draw_7seg_digit(cursor_x, y, char, color, bg, w, h, t)
            cursor_x += w + gap

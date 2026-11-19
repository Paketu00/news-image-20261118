import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 226)
INK = (18, 18, 20)
RED = (178, 34, 42)
BLUE = (24, 62, 122)
GOLD = (214, 164, 32)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
SKY = (178, 205, 228)
GREEN = (34, 110, 72)

buf = bytearray(W * H * 3)


def set_px(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = col[0]
        buf[i + 1] = col[1]
        buf[i + 2] = col[2]


def fill_rect(x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, col)


def rect_outline(x, y, w, h, col, t=2):
    fill_rect(x, y, w, t, col)
    fill_rect(x, y + h - t, w, t, col)
    fill_rect(x, y, t, h, col)
    fill_rect(x + w - t, y, t, h, col)


def fill_circle(cx, cy, r, col):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                set_px(xx, yy, col)


def circle_outline(cx, cy, r, col, t=3):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if (r - t) * (r - t) <= d2 <= (r + t) * (r + t):
                set_px(xx, yy, col)


FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
}


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, col):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            line = glyph[row]
            for c in range(5):
                if line[c] == "#":
                    fill_rect(cx + c * scale, y + row * scale, scale, scale, col)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, col):
    w = text_width(s, scale)
    draw_text((W - w) // 2, y, s, scale, col)


def wrap(s, scale, max_w):
    words = s.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, col, max_w, line_gap=6):
    for line in wrap(s, scale, max_w):
        draw_text(x, y, line, scale, col)
        y += 7 * scale + line_gap
    return y


def hline(y, col=INK, t=3):
    fill_rect(36, y, W - 72, t, col)


def story(x, y, w, label, label_col, headline, body):
    fill_rect(x, y, text_width(label, 2) + 16, 22, label_col)
    draw_text(x + 8, y + 4, label, 2, WHITE)
    y += 32
    y = draw_wrapped(x, y, headline, 3, INK, w, 5)
    y += 2
    y = draw_wrapped(x, y, body, 2, (52, 52, 52), w, 5)
    return y


def brief(x, y, w, label, label_col, headline, body):
    fill_rect(x, y, text_width(label, 2) + 16, 22, label_col)
    draw_text(x + 8, y + 4, label, 2, WHITE)
    y += 30
    y = draw_wrapped(x, y, headline, 2, INK, w, 5)
    y += 2
    y = draw_wrapped(x, y, body, 2, (52, 52, 52), w, 5)
    return y


def draw_globe(cx, cy, r):
    fill_circle(cx, cy, r, SKY)
    circle_outline(cx, cy, r, BLUE, 3)
    for dx in (-r // 2, 0, r // 2):
        w2 = int((r * r - dx * dx) ** 0.5)
        for yy in range(cy - w2, cy + w2 + 1, 4):
            set_px(cx + dx, yy, BLUE)
            set_px(cx + dx + 1, yy, BLUE)
    for dy in (-r // 2, 0, r // 2):
        w2 = int((r * r - dy * dy) ** 0.5)
        for xx in range(cx - w2, cx + w2 + 1, 4):
            set_px(xx, cy + dy, BLUE)
            set_px(xx, cy + dy + 1, BLUE)
    fill_circle(cx - 28, cy - 18, 13, GREEN)
    fill_circle(cx + 24, cy + 8, 16, GREEN)
    fill_circle(cx + 4, cy - 34, 9, GREEN)


def build():
    fill_rect(0, 0, W, H, PAPER)
    rect_outline(18, 18, W - 36, H - 36, INK, 4)
    rect_outline(28, 28, W - 56, H - 56, INK, 1)

    fill_rect(36, 44, W - 72, 8, RED)
    draw_centered(64, "THE WORLD IN ONE PAGE", 6, INK)
    fill_rect(36, 122, W - 72, 34, INK)
    draw_centered(131, "WEDNESDAY, NOVEMBER 18, 2026 - ALL THE NEWS IN ONE IMAGE", 2, WHITE)
    hline(172)

    draw_text(48, 186, "TOP STORY - SHENZHEN, CHINA", 3, RED)
    draw_text(48, 226, "TRUMP, XI AND PUTIN", 6, INK)
    draw_text(48, 278, "MEET IN SHENZHEN", 6, INK)
    draw_globe(884, 262, 58)
    deck = (
        "FIRST THREE-WAY SUMMIT AT THE APEC GATHERING. THE LEADERS ARE SET TO "
        "DISCUSS UKRAINE, IRAN, TRADE AND NUCLEAR ARMS AFTER XI GREETED TRUMP "
        "AT THE AIRPORT AND XI AND PUTIN COORDINATED THEIR POSITIONS."
    )
    draw_wrapped(48, 344, deck, 2, (52, 52, 52), 900, 6)
    hline(430)

    story(
        48, 448, 440, "MIDDLE EAST", RED,
        "IRAN HITS US BASES IN KUWAIT AND BAHRAIN",
        "STRIKES FOLLOW US ATTACKS ON QESHM ISLAND. BAHRAIN SAYS IT "
        "INTERCEPTED IRANIAN ATTACKS FOR A THIRD TIME IN A WEEK, AND "
        "SHIPPING THROUGH THE STRAIT OF HORMUZ STAYED DISRUPTED.",
    )
    story(
        536, 448, 440, "EUROPE", BLUE,
        "UKRAINE HITS CRIMEAN BRIDGE AGAIN",
        "A THIRD STRIKE IN A WEEK CRIPPLED THE ROAD LINK TO CRIMEA, "
        "IN A BLOW FOR PUTIN ON THE EVE OF THE SHENZHEN SUMMIT.",
    )
    fill_rect(512, 448, 2, 190, GREY)
    hline(652)

    story(
        48, 670, 440, "MIDDLE EAST", RED,
        "GAZA TRUCE AT RISK OF COLLAPSE",
        "CEASEFIRE MONITORS WARNED THE DEAL COULD COLLAPSE WITHOUT "
        "ACTION, AS ISRAELI TANKS CROSSED THE YELLOW LINE IN GAZA.",
    )
    story(
        536, 670, 440, "UNITED STATES", BLUE,
        "ALASKA FLIPS THE U.S. SENATE",
        "MARY PELTOLA DEFEATED INCUMBENT DAN SULLIVAN, GIVING "
        "DEMOCRATS A PROJECTED 56-44 MAJORITY IN THE NEW SENATE.",
    )
    fill_rect(512, 670, 2, 170, GREY)
    hline(844)

    brief(
        48, 856, 288, "TECH", GREEN,
        "ANTHROPIC'S RECORD IPO",
        "AT $83 A SHARE, A RECORD. NVIDIA: NO RETURN FOR HUANG.",
    )
    brief(
        368, 856, 288, "SOUTH ASIA", GOLD,
        "CYCLONE AKVAN: ODISHA ON ALERT",
        "EVACUATIONS IN SOUTH ODISHA. SCHOOLS SHUT.",
    )
    brief(
        688, 856, 288, "BANGLADESH", BLUE,
        "BANGLADESH UNREST GROWS",
        "PARAMILITARY DEPLOYED OVER HASINA RETURN PLAN.",
    )
    fill_rect(344, 856, 2, 100, GREY)
    fill_rect(664, 856, 2, 100, GREY)

    fill_rect(36, 966, W - 72, 26, GOLD)
    draw_centered(972, "TOMORROW: GTA VI HITS SHELVES - SOURCES: REUTERS, AP, AFP, AL JAZEERA", 2, INK)


def png_bytes():
    raw = bytearray()
    row_len = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * row_len:(y + 1) * row_len])

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    build()
    data = png_bytes()
    written = []
    for path in ("/output/entry.png", "entry.png"):
        try:
            folder = os.path.dirname(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            written.append(path)
        except OSError:
            pass
    if not written:
        raise SystemExit("could not write entry.png anywhere")
    print("wrote", ", ".join(written), len(data), "bytes")


if __name__ == "__main__":
    main()

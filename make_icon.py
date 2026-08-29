from PIL import Image, ImageDraw
import os

os.makedirs("ui/assets", exist_ok=True)

# Create 256x256 RGBA image
img = Image.new('RGBA', (256, 256), color=(15, 15, 18, 255))
draw = ImageDraw.Draw(img)

# 1. Draw top & bottom hazard warning bands
stripe_w = 16
for i in range(-stripe_w, 256, stripe_w * 2):
    # Top stripes
    draw.polygon([
        (i, 0), (i + stripe_w, 0),
        (i + stripe_w - 12, 12), (i - 12, 12)
    ], fill=(243, 255, 0, 255))
    # Bottom stripes
    draw.polygon([
        (i + 12, 244), (i + stripe_w + 12, 244),
        (i + stripe_w, 256), (i, 256),
    ], fill=(243, 255, 0, 255))

# 2. Draw outer ZZZ border frame (thick neon cyan)
draw.rectangle([6, 6, 249, 249], outline=(0, 240, 255, 255), width=4)

# 3. Draw ZZZ cassette player in the center (neon pink body with cyan chromatic offset)
# Offset shadow (cyan)
draw.rounded_rectangle([44, 74, 214, 174], radius=12, fill=(15, 15, 18, 255), outline=(0, 240, 255, 150), width=4)
# Main body (pink)
draw.rounded_rectangle([40, 70, 210, 170], radius=12, fill=(15, 15, 18, 255), outline=(255, 0, 85, 255), width=5)

# Cassette transparent window
draw.rectangle([65, 95, 185, 145], fill=(25, 25, 30, 255), outline=(243, 255, 0, 255), width=2)

# Spools (reels)
# Left Spool
draw.ellipse([80, 107, 106, 133], fill=(36, 36, 46, 255), outline=(255, 255, 255, 255), width=2)
# Right Spool
draw.ellipse([144, 107, 170, 133], fill=(36, 36, 46, 255), outline=(255, 255, 255, 255), width=2)

# Spool spokes (draw a star/gears inside spools)
for spool_x in [93, 157]:
    for dx, dy in [(-8, 0), (8, 0), (0, -8), (0, 8), (-5, -5), (5, 5), (5, -5), (-5, 5)]:
        draw.line([(spool_x, 120), (spool_x + dx, 120 + dy)], fill=(243, 255, 0, 255), width=2)

# Tiny REC light (red)
draw.ellipse([194, 80, 200, 86], fill=(255, 0, 85, 255))

# Save as both PNG and ICO
img.save("ui/assets/icon.png", format="PNG")

# Convert to standard ICO format
img_ico = Image.open("ui/assets/icon.png")
img_ico.save("ui/assets/icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

print("Successfully generated ZZZ theme icon.png and icon.ico!")

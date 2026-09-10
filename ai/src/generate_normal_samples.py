import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

train_normal = Path('ai/dataset/train/Normal')
val_normal = Path('ai/dataset/validation/Normal')
test_normal = Path('ai/dataset/test/Normal')

def create_pv_sample(idx, base_color, busbar_color, n_busbars=2, n_fingers=16, glare=False):
    im = Image.new('RGB', (224, 224), color=base_color)
    d = ImageDraw.Draw(im)
    spacing = 224 // (n_busbars + 1)
    for b in range(1, n_busbars + 1):
        x = b * spacing + (idx % 5 - 2)
        d.line([(x, 0), (x, 224)], fill=busbar_color, width=2)
    f_spacing = max(6, 224 // n_fingers)
    f_color = tuple(min(255, c + 35) for c in base_color)
    for f in range(2, 224, f_spacing):
        d.line([(0, f), (224, f)], fill=f_color, width=1)
    if glare:
        glare_overlay = Image.new('RGBA', (224, 224), (255, 255, 255, 0))
        gd = ImageDraw.Draw(glare_overlay)
        gx, gy = 160 + (idx % 20), 40 + (idx % 20)
        gd.ellipse([(gx-40, gy-40), (gx+40, gy+40)], fill=(255, 255, 255, 50))
        im = Image.alpha_composite(im.convert('RGBA'), glare_overlay).convert('RGB')
    return im

base_colors = [
    (20, 45, 110),
    (15, 35, 95),
    (30, 60, 140),
    (25, 28, 35),
    (35, 40, 50),
    (40, 70, 150),
    (18, 30, 75),
]

busbar_colors = [
    (210, 215, 225),
    (180, 185, 195),
    (240, 240, 245),
]

for i in range(150):
    c = base_colors[i % len(base_colors)]
    bc = busbar_colors[i % len(busbar_colors)]
    nb = 2 if i % 2 == 0 else 3
    nf = 18 if i % 3 == 0 else 24
    glare = (i % 4 == 0)
    im = create_pv_sample(i, c, bc, nb, nf, glare)
    im.save(train_normal / f'Normal_pv_{i:04d}.png')

for i in range(20):
    c = base_colors[(i+2) % len(base_colors)]
    bc = busbar_colors[(i+1) % len(busbar_colors)]
    im = create_pv_sample(i+200, c, bc, 2, 20, i % 3 == 0)
    im.save(val_normal / f'Normal_pv_val_{i:04d}.png')

for i in range(20):
    c = base_colors[(i+4) % len(base_colors)]
    bc = busbar_colors[(i+2) % len(busbar_colors)]
    im = create_pv_sample(i+300, c, bc, 3, 22, i % 2 == 0)
    im.save(test_normal / f'Normal_pv_test_{i:04d}.png')

print('Generated and saved diverse solar PV samples for Normal class.')

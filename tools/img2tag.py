"""Compact pixel-art guild tag: 1px div, 1px offsets, hex colours (about half the size of img2tag.py output).

usage: python img2tag_compact.py input.png [max_width_px=112] [lanczos|nearest] > tag.html
Each art pixel is exactly 1 CSS px, so scale the box via the wrapper's width/height if you need it bigger.
"""
import sys
from PIL import Image
src=sys.argv[1]; maxw=int(sys.argv[2]) if len(sys.argv)>2 else 112; mode=sys.argv[3] if len(sys.argv)>3 else "lanczos"
im=Image.open(src).convert('RGBA')
im=im.crop(im.getchannel('A').getbbox() or (0,0,*im.size))
if im.width>maxw: im=im.resize((maxw,max(1,round(im.height*maxw/im.width))),Image.NEAREST if mode=="nearest" else Image.LANCZOS)
def hexc(r,g,b,a):
    h=f"#{r:02x}{g:02x}{b:02x}"
    if a<255: h+=f"{a:02x}"
    if a==255 and h[1]==h[2] and h[3]==h[4] and h[5]==h[6]: h=f"#{h[1]}{h[3]}{h[5]}"   # 3-digit shorthand
    return h
sh=[]
for y in range(im.height):
    for x in range(im.width):
        r,g,b,a=im.getpixel((x,y))
        if a<64: continue
        sh.append(f"{x or 0}{'px' if x else ''} {y or 0}{'px' if y else ''} {hexc(r,g,b,a)}")
sys.stderr.write(f"{im.width}x{im.height} art px, {len(sh)} shadows\n")
print(f'<div style="position: absolute; top: 0; left: 0; width: 1px; height: 1px; box-shadow: {",".join(sh)}"></div>')

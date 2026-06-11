import os
from PIL import Image

def create_pwa_icon(source_path, target_dir, size, padding=40):
    try:
        # Open the source image
        src_img = Image.open(source_path).convert("RGBA")
        
        # Calculate aspect ratio
        src_w, src_h = src_img.size
        
        # Create a white background square image
        bg = Image.new("RGBA", (size, size), (255, 255, 255, 255))
        
        # Determine how to scale the source image to fit within the padding
        max_dim = size - padding
        scale = min(max_dim / src_w, max_dim / src_h)
        
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)
        
        # Resize source image smoothly
        src_img_resized = src_img.resize((new_w, new_h), Image.LANCZOS)
        
        # Calculate position to paste (center)
        paste_x = (size - new_w) // 2
        paste_y = (size - new_h) // 2
        
        # Paste using the alpha channel as a mask
        bg.paste(src_img_resized, (paste_x, paste_y), src_img_resized)
        
        # Save
        target_path = os.path.join(target_dir, f"pwa-{size}x{size}.png")
        bg.save(target_path, "PNG")
        print(f"Created {target_path}")
    except Exception as e:
        print(f"Error creating icon size {size}: {e}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Muquissi\Documents\Eduka-Angola"
    # Try Eduka.png first, fallback to logo1.png
    src1 = os.path.join(base_dir, "static", "assets", "images", "logo", "Eduka.png")
    src2 = os.path.join(base_dir, "static", "assets", "images", "logo", "logo1.png")
    
    src = src1 if os.path.exists(src1) else src2
    print(f"Using source image: {src}")
    
    target_dir = os.path.join(base_dir, "static", "assets", "images", "icons")
    os.makedirs(target_dir, exist_ok=True)
    
    create_pwa_icon(src, target_dir, 192, padding=30)
    create_pwa_icon(src, target_dir, 512, padding=80)

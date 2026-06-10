import os
from PIL import Image

def resize_image(input_path, output_dir, size, name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        img = Image.open(input_path)
        img = img.convert("RGBA")
        
        # Calculate padding to make it square without stretching
        width, height = img.size
        new_dim = max(width, height)
        
        # Create a new image with transparent background
        new_img = Image.new("RGBA", (new_dim, new_dim), (0, 0, 0, 0))
        
        # Paste the original image in the center
        paste_x = (new_dim - width) // 2
        paste_y = (new_dim - height) // 2
        new_img.paste(img, (paste_x, paste_y), img)
        
        # Resize to target size
        resized_img = new_img.resize((size, size), Image.Resampling.LANCZOS)
        
        output_path = os.path.join(output_dir, name)
        resized_img.save(output_path, format="PNG")
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error generating {name}: {e}")

if __name__ == "__main__":
    input_image = r"c:\Users\Muquissi\Documents\Eduka-Angola\static\assets\images\Logo1.png"
    output_dir = r"c:\Users\Muquissi\Documents\Eduka-Angola\static\assets\images\icons"
    
    resize_image(input_image, output_dir, 192, "pwa-192x192.png")
    resize_image(input_image, output_dir, 512, "pwa-512x512.png")

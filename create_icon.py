import sys
from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with a white background
    img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw a rounded rectangle (blue background)
    draw.rounded_rectangle([(10, 10), (246, 246)], radius=40, fill='#409EFF', outline=None)

    # Draw a "check" mark or "A" for Answer
    # Let's draw a stylized 'A'
    draw.text((60, 20), "A", fill="white", font_size=200) # This requires a font, might fail if default font not scalable
    
    # Alternative: Draw a simple checkmark
    # Points for checkmark
    points = [(60, 130), (100, 170), (200, 70)]
    draw.line(points, fill='white', width=30, joint='curve')

    # Save as .ico
    try:
        img.save('resources/icons/icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("Icon created successfully.")
    except Exception as e:
        print(f"Error creating icon: {e}")

if __name__ == "__main__":
    create_icon()

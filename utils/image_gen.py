from PIL import Image, ImageDraw, ImageFont
import os

def generate_result_image(animal, username=None):
    background_color = (10, 30, 40)
    text_color = (255, 255, 255)
    width, height = 800, 600
    font_path = "arial.ttf"

    img = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(font_path, 48)
        font_text = ImageFont.truetype(font_path, 28)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    title = f"Ты — {animal['name']}!"
    desc = animal['description']
    user_text = f"@{username}" if username else ""

    draw.text((40, 80), title, font=font_title, fill=text_color)
    draw.text((40, 160), desc, font=font_text, fill=text_color)
    draw.text((40, 500), user_text, font=font_text, fill=(180, 180, 180))

    result_path = "result.jpg"
    img.save(result_path)
    return result_path
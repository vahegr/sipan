import io
import os
from math import floor

from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import reshape 
from bidi.algorithm import get_display
from sipan.settings import BASE_DIR

dpi = 300
width = floor(8.5 * dpi / 2.54)
height = floor(6 * dpi / 2.54)


def cm_to_px(x):
    return floor(x * dpi / 2.54)


def center_pos(x, y, text, font):
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (width, height), (255, 255, 255)))
    font_size = font.size
    len = tmp_draw.textlength(text, font=font)
    return (x-len/2, y-font_size/2)


def generate_card(fullname_am, fullname_fa, section_text, national_code, user_id):
    logo_path = os.path.join(BASE_DIR, 'assets', 'logo.png')
    logo_image = Image.open(logo_path).convert('RGB')
    logo_size = (cm_to_px(2), cm_to_px(2))

    card = Image.new("RGB", (width, height), (255, 255, 255))
    profile_holder = Image.new("RGB", (cm_to_px(2.3), cm_to_px(3.5)), (123, 22, 11))

    section_font_size = cm_to_px(0.7)
    font_size = cm_to_px(0.3)
    name_font_size = cm_to_px(0.4)
    font = ImageFont.truetype("arial.ttf", font_size)
    name_font = ImageFont.truetype("tahoma.ttf", name_font_size)
    section_font = ImageFont.truetype("arial.ttf", section_font_size)

    draw = ImageDraw.Draw(card)

    # logo and name
    draw.rectangle(((cm_to_px(5.2), cm_to_px(1.2)), (width, cm_to_px(1.4))), fill="black")
    text_fa = get_display(reshape("انجمن فرهنگی ورزشی\nارامنــه سیــپــان"))
    draw.text((cm_to_px(5.3), cm_to_px(0.5)), "ՀԱՅ ՄՇԱԿՈՒԹԱՅԻՆ\n«ՍԻՓԱՆ» ՄԻՈՒԹԻՒՆ", font=font,  fill=(0, 0, 0))
    draw.text((cm_to_px(5.3), cm_to_px(1.5)), text_fa, font=font,  fill=(0, 0, 0))
    card.paste(logo_image.resize(logo_size, Image.LANCZOS), (cm_to_px(3), cm_to_px(0.4)))

    # Section
    draw.rectangle(((0, cm_to_px(5)), (width, height)), fill="black")
    draw.text(center_pos(width/2, cm_to_px(5.5), section_text, section_font), section_text, font=section_font,  fill=(255,255,255))

    # profile and texts
    card.paste(profile_holder, (cm_to_px(0.4), cm_to_px(0.4)))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(4.7), str(national_code), font), str(national_code), font=font,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(4.2), str(user_id), font), str(user_id), font=font,  fill=(0, 0, 0))

    # name
    text_fa = get_display(reshape(fullname_fa))
    draw.text(center_pos(cm_to_px(6), cm_to_px(3.5), fullname_am, name_font), fullname_am, font=name_font,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(6), cm_to_px(4), text_fa, name_font), text_fa, font=name_font,  fill=(0, 0, 0))

    img_byte_arr = io.BytesIO()
    card.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

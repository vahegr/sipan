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
    len_text = tmp_draw.textlength(text, font=font)
    return (x-len_text/2, y-font_size/2)


def get_font(text, font_name, initial_size, max_len):
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (width, height), (255, 255, 255)))
    current_size = initial_size
    font = ImageFont.truetype(font_name, current_size)
    curr_len = tmp_draw.textlength(text, font=font)
    while curr_len > max_len:
        current_size -= 1
        font = ImageFont.truetype(font_name, current_size)
        curr_len = tmp_draw.textlength(text, font=font)
    return font


def scale_to_fit_box(image_path, box_width, box_height):
    profile_holder = Image.new("RGB", (box_width, box_height), (255, 255, 255))
    image = Image.open(image_path)
    image_width, image_height = image.size

    scale_factor = box_height/image_height
    new_height = box_height
    new_width = floor(scale_factor*image_width)

    resized_image = image.resize((new_width, new_height))
    profile_holder.paste(resized_image, ((profile_holder.width - new_width)//2, (profile_holder.height - new_height)//2) )
    return profile_holder


def generate_card(image_path, fullname_am, fullname_fa, section_text, section_color, national_code, user_id):
    logo_path = os.path.join(BASE_DIR, 'assets', 'logo.png')
    logo_image = Image.open(logo_path).convert('RGB')
    logo_size = (cm_to_px(2), cm_to_px(2))

    card = Image.new("RGB", (width, height), (255, 255, 255))
    if os.path.exists(image_path):
        profile_holder = scale_to_fit_box(image_path, cm_to_px(2.3), cm_to_px(3.5))
    else:
        profile_holder = Image.new("RGB", (cm_to_px(2.3), cm_to_px(3.5)), (255, 255, 255))

    section_font_size = cm_to_px(0.5)
    font_size = cm_to_px(0.3)
    font = ImageFont.truetype("arial.ttf", font_size)
    section_font = ImageFont.truetype("arial.ttf", section_font_size)
    
    draw = ImageDraw.Draw(card)

    # logo and name
    draw.rectangle(((cm_to_px(5.2), cm_to_px(1.2)), (width, cm_to_px(1.4))), fill="black")
    text_fa = get_display(reshape("انجمن فرهنگی ورزشی\nارامنــه سیــپــان"))
    draw.text((cm_to_px(5.3), cm_to_px(0.5)), "ՀԱՅ ՄՇԱԿՈՒԹԱՅԻՆ\n«ՍԻՓԱՆ» ՄԻՈՒԹԻՒՆ", font=font,  fill=(0, 0, 0))
    draw.text((cm_to_px(5.3), cm_to_px(1.5)), text_fa, font=font,  fill=(0, 0, 0))
    card.paste(logo_image.resize(logo_size, Image.LANCZOS), (cm_to_px(3), cm_to_px(0.4)))

    # Section
    draw.rectangle(((0, cm_to_px(5)), (width, height)), fill=section_color)
    draw.text(center_pos(width/2, cm_to_px(5.41), section_text, section_font), section_text, font=section_font,  fill=(255,255,255))

    # profile and texts
    card.paste(profile_holder, (cm_to_px(0.4), cm_to_px(0.4)))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(4.7), str(national_code), font), str(national_code), font=font,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(4.2), str(user_id), font), str(user_id), font=font,  fill=(0, 0, 0))

    # name
    text_fa = get_display(reshape(fullname_fa))
    name_font_size = cm_to_px(0.4)
    name_font_size1 = get_font(text_fa, "tahoma.ttf", name_font_size, cm_to_px(4))
    name_font_size2 = get_font(fullname_am, "tahoma.ttf", name_font_size, cm_to_px(4))
    draw.text(center_pos(cm_to_px(5.5), cm_to_px(3.5), fullname_am, name_font_size2), fullname_am, font=name_font_size2,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(5.5), cm_to_px(4), text_fa, name_font_size1), text_fa, font=name_font_size1,  fill=(0, 0, 0))

    img_byte_arr = io.BytesIO()
    card.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

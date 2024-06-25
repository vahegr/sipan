import io
import os
import platform

from math import floor, ceil

from PIL import Image, ImageDraw, ImageFont, ImageOps
from arabic_reshaper import reshape 
from bidi.algorithm import get_display

from sipan.settings import BASE_DIR
from django.shortcuts import get_object_or_404
from subscription.models import Subscription

dpi = 300
width = floor(8.5 * dpi / 2.54)
height = floor(5.4 * dpi / 2.54)

dash = 6
dash_whitespace = 5
dash_color = 'black'
dash_width = 1


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


def prepare_profile_image(image_path, box_width, box_height):
    profile_holder = Image.new("RGB", (box_width, box_height), (255, 255, 255))
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)
    image_width, image_height = image.size

    scale_factor = box_height/image_height
    new_height = box_height
    new_width = floor(scale_factor*image_width)

    resized_image = image.resize((new_width, new_height))
    profile_holder.paste(resized_image, ((profile_holder.width - new_width)//2, (profile_holder.height - new_height)//2) )
    return profile_holder

def generate_page(data):
    if len(data) > 100 or len(data) == 0:
        return b''
    page_w = cm_to_px(21)
    page_h = cm_to_px(29.7)
    margin_x_page = cm_to_px(1)
    margin_y_page = cm_to_px(1)
    margin_x = cm_to_px(0.5)
    margin_y = cm_to_px(0.5)
    col_count = (page_w+margin_x-2*margin_x_page) // (width + margin_x)
    row_count = (page_h+margin_y-2*margin_y_page) // (height + margin_y)
    count = col_count * row_count
    pages_count = ceil(len(data) / count)
    pages = []
    card_count = len(data)
    for _ in range(pages_count):
        pages.append(Image.new('RGB', (page_w, page_h), (255, 255, 255)))

    for n in range(card_count):
        col = n % col_count
        row = (n // col_count) % row_count
        page_n = n // count

        card_image = generate_card_image(data[n]['user'], data[n]['year'])
        pages[page_n].paste(card_image, (margin_x_page+col*(width+margin_x), margin_y_page+row*(height+margin_y)))

    pdf_bytes = io.BytesIO()
    pages[0].save(pdf_bytes, format='PDF', save_all=True, append_images=pages[1:])
    pdf_bytes.name = "cards.pdf"
    return pdf_bytes.getvalue()

def generate_card(user, section_year):
    img_byte_arr = io.BytesIO()
    image = generate_card_image(user, section_year)
    image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()


def generate_card_image(user, section_year):
    if user.image:
        image_path = user.image.path
    else:
        image_path = ""
    fullname_am, fullname_fa, section_text, section_color, national_code, user_id = user.full_name, user.first_name_fa + ' ' + user.last_name_fa, f"{section_year.section.name} {section_year.year}", section_year.section.color, user.national_code, user.id

    isWindows = platform.system() == "Windows"
    logo_path = os.path.join(BASE_DIR, 'assets', 'logo.png')
    logo_image = Image.open(logo_path).convert('RGB')
    logo_size = (cm_to_px(2), cm_to_px(2))

    card = Image.new("RGB", (width, height), (255, 255, 255))
    if os.path.exists(image_path):
        profile_holder = prepare_profile_image(image_path, cm_to_px(2.3), cm_to_px(3))
    else:
        profile_holder = Image.new("RGB", (cm_to_px(2.3), cm_to_px(3)), (255, 255, 255))

    section_font_size = cm_to_px(0.5)
    font_size = cm_to_px(0.3)
    font = ImageFont.truetype(os.path.join(BASE_DIR, 'assets', 'arial.ttf'), font_size)
    section_font = ImageFont.truetype(os.path.join(BASE_DIR, 'assets', 'arial.ttf'), section_font_size)

    draw = ImageDraw.Draw(card)

    # logo and name
    draw.rectangle(((cm_to_px(5.2), cm_to_px(1.2)), (width, cm_to_px(1.4))), fill="black")
    text_logo_fa = "انجمن فرهنگی ورزشی\nارامنــه سیــپــان"
    text_fa = get_display(reshape(text_logo_fa)) if isWindows else reshape(text_logo_fa)
    draw.text((cm_to_px(5.3), cm_to_px(0.5)), "ՀԱՅ ՄՇԱԿՈՒԹԱՅԻՆ\n«ՍԻՓԱՆ» ՄԻՈՒԹԻՒՆ", font=font,  fill=(0, 0, 0))
    draw.text((cm_to_px(5.3), cm_to_px(1.5)), text_fa, font=font,  fill=(0, 0, 0))
    card.paste(logo_image.resize(logo_size, Image.LANCZOS), (cm_to_px(3), cm_to_px(0.4)))

    # Section
    draw.rectangle(((0, cm_to_px(4.4)), (width, height)), fill=section_color)
    draw.text(center_pos(width/2, cm_to_px(4.81), section_text, section_font), section_text, font=section_font,  fill=(255,255,255))

    # profile and texts
    card.paste(profile_holder, (cm_to_px(0.4), cm_to_px(0.4)))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(4.1), str(national_code), font), str(national_code), font=font,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(1.5), cm_to_px(3.7), str(user_id), font), str(user_id), font=font,  fill=(0, 0, 0))

    # name
    text_fa = get_display(reshape(fullname_fa)) if isWindows else reshape(fullname_fa)
    name_font_size = cm_to_px(0.4)
    name_font_size1 = get_font(text_fa, os.path.join(BASE_DIR, 'assets', 'arial.ttf'), name_font_size, cm_to_px(4))
    name_font_size2 = get_font(fullname_am, os.path.join(BASE_DIR, 'assets', 'arial.ttf'), name_font_size, cm_to_px(4))
    draw.text(center_pos(cm_to_px(5.5), cm_to_px(3.2), fullname_am, name_font_size2), fullname_am, font=name_font_size2,  fill=(0, 0, 0))
    draw.text(center_pos(cm_to_px(5.5), cm_to_px(3.7), text_fa, name_font_size1), text_fa, font=name_font_size1,  fill=(0, 0, 0))

    # dashed line around box
    dashed_card = Image.new("RGB", (width+dash_width*2, height+dash_width*2), (255, 255, 255))
    dashed_draw = ImageDraw.Draw(dashed_card)
    dashed_card.paste(card, (1, 1))
    for i in range(width//(dash+dash_whitespace)+4):
        dashed_draw.line(((i-1)*(dash+dash_whitespace), 0, min(i*dash+(i-1)*dash_whitespace, width), 0), width=dash_width, fill=dash_color)
        dashed_draw.line(((i-1)*(dash+dash_whitespace), height+dash_width, min(i*dash+(i-1)*dash_whitespace, width), height+dash_width), width=dash_width, fill=dash_color)

    for i in range(height//(dash+dash_whitespace)+4):
        dashed_draw.line((0, (i-1)*(dash+dash_whitespace), 0, min(i*dash+(i-1)*dash_whitespace, width)), width=dash_width, fill=dash_color)
        dashed_draw.line((width+dash_width, (i-1)*(dash+dash_whitespace), width+dash_width, min(i*dash+(i-1)*dash_whitespace, width+dash_width*2)), width=dash_width, fill=dash_color)

    return dashed_card

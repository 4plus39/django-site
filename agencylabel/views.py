from django.shortcuts import render
from django.views.generic import View

# Create your views here.
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from .const import *
import sys
import os
import uuid
import pygame
from .models import Label, LabelSize, Icon, Warning, CompanyLogo, MadeIn, Area
import math
import re
from django.core.files.storage import FileSystemStorage


text_position_x = 0

text_position_y = 0

label_position = [
[(X, Y), (X+COL_GAP, Y), (X+COL_GAP*2, Y), (X+COL_GAP*3, Y), (X+COL_GAP*4, Y)],
[(X, Y+ROW_GAP), (X+COL_GAP, Y+ROW_GAP), (X+COL_GAP*2, Y+ROW_GAP), (X+COL_GAP*3, Y+ROW_GAP), (X+COL_GAP*4, Y+ROW_GAP)],
[(X, Y+ROW_GAP*2), (X+COL_GAP, Y+ROW_GAP*2), (X+COL_GAP*2, Y+ROW_GAP*2), (X+COL_GAP*3, Y+ROW_GAP*2), (X+COL_GAP*4, Y+ROW_GAP*2)],
[(X, Y+ROW_GAP*3), (X+COL_GAP, Y+ROW_GAP*3), (X+COL_GAP*2, Y+ROW_GAP*3), (X+COL_GAP*3, Y+ROW_GAP*3), (X+COL_GAP*4, Y+ROW_GAP*3)],
]

index = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]

def img2rgba(path):
    img = Image.open(path)
    rgba = img.convert('RGBA')
    return rgba

def resize_img_half(img):
    img_width, img_height = img.size
    img = img.resize((int(img_width*LABEL_SIZE), int(img_height*LABEL_SIZE)))
    # print(img.size)
    return img

def resize_img_80_percent(img):
    img_width, img_height = img.size
    img = img.resize((int(img_width*0.8), int(img_height*0.8)))
    # print(img.size)
    return img

def resize_img(img, percent):
    img_width, img_height = img.size
    img = img.resize((int(img_width*percent*0.01), int(img_height*percent*0.01)))
    # print(img.size)
    return img

def text_paste(img, label_path):
    global text_position_x, text_position_y
    print("text_position_x= ", text_position_x)
    print("text_position_y= ", text_position_y)
    label = img2rgba(label_path)
    img.paste(label, (text_position_x, text_position_y), label)
    text_position_y += label.size[1]
    # text_position_y += 2

def label_paste(img, label_path):
    label = img2rgba(label_path)
    label = resize_img_half(label)
    y, x = visit(label)
    
    if x != 99:
        img.paste(label, label_position[y][x], label)
        return 1
    else:
        print("No space for label '%s'" % (label_path[6::]))
        return 0

def all_paste(img, sub_img, coor, level):
    # sub_img = img2rgba(sub_img_path)
    # print("label img size = ", img.size)
    # print("icon img size = ", sub_img.size)
    x, y = visit2(sub_img, coor, level)

    if x != 9999:
        img.paste(sub_img, (x*UNIT, y*UNIT), sub_img)
        return 1
    else:
        # No space for sub_img
        return 0

def all_paste_icon(img, sub_img_path):
    sub_img = img2rgba(sub_img_path)
    sub_img = resize_img(sub_img, 35)
    x, y = visit2(sub_img)

    if x != 9999:
        img.paste(sub_img, (15+x*UNIT, 10+y*UNIT), sub_img)
        return 1
    else:
        print("No space")
        return 0

def visit(img):
    wid, hei = img.size
    unit_wid = round(wid/118)
    unit_hei = round(hei/118)

    # print(img.size, unit_wid, unit_hei)

    # 1:1
    # 20x20mm
    if unit_wid == 1 and unit_hei == 1:
        for y in range(ROW):
            for x in range(COLUMN):
                if index[y][x] == 0:
                    index[y][x] = 1
                    return y, x
        return 99, 99
    # 2:1
    # 30x20mm or 40x20mm
    elif unit_wid == 2 and unit_hei == 1:
        for y in range(ROW):
            for x in range(5):
                if x+1 < COLUMN:
                    if index[y][x] == 0 and index[y][x+1] == 0:
                        index[y][x] = 1
                        index[y][x+1] = 1
                        return y, x
        return 99, 99
    # 3:1
    # 60x20mm
    elif unit_wid == 3 and unit_hei == 1:
        for y in range(ROW):
            for x in range(COLUMN):
                if x + 2 < COLUMN:
                    if index[y][x] == 0 and index[y][x+1] == 0 and index[y][x+2] == 0:
                        index[y][x] = 1
                        index[y][x+1] = 1
                        index[y][x+2] = 1
                        return y, x
        return 99, 99
    # 1:2
    # 20x30mm
    elif unit_wid == 1 and unit_hei == 2:
        for y in range(ROW):
            for x in range(COLUMN):
                if y + 1 < ROW:
                    if index[y][x] == 0 and index[y+1][x] == 0:
                        index[y][x] = 1
                        index[y+1][x] = 1
                        return y, x
        return 99, 99
    # 2:2
    # 30x30mm or 40x30
    elif unit_wid == 2 and unit_hei == 2:
        for y in range(ROW):
            for x in range(COLUMN):
                if y + 1 < ROW and x + 1 < COLUMN:
                    if index[y][x] == 0 and index[y+1][x] == 0 and index[y][x+1] == 0 and index[y+1][x+1] == 0:
                        index[y][x] = 1
                        index[y+1][x] = 1
                        index[y][x+1] = 1
                        index[y+1][x+1] = 1
                        return y, x
        return 99, 99
    else:
        print("No compatible image")
        exit()

def visit2(img, coor, level):
    wid, hei = img.size
    # print(wid, hei)
    unit_wid = math.ceil(wid/UNIT) + level
    unit_hei = math.ceil(hei/UNIT) + level

    # print("len(coor[0]) = ", len(coor[0]))
    # print("len(coor) = ", len(coor))
    # print("range(unit_wid-1) = ",range(unit_wid))
    # print("range(unit_hei-1) = ", range(unit_hei))

    '''
    for y in range(len(coor)):
        for x in range(len(coor[0])):
    '''
    for x in range(len(coor[0])):
        for y in range(len(coor)):
            # Find start dot to put image
            if coor[y][x] == 0:
                flag = 1
                # Check if it has enough space for image
                for m in range(unit_wid):
                    for n in range(unit_hei):
                        if x+m >= len(coor[0]):
                            flag = 0
                            break
                        elif y+n >= len(coor):
                            flag = 0
                            break
                        elif coor[y+n][x+m] == 1:
                            flag = 0
                            break
                        else:
                            # print('no enough space')
                            pass
                if flag == 1:
                    # print('find it!!!')
                    for m in range(unit_wid):
                        for n in range(unit_hei):
                            coor[y+n][x+m] = 1
                    '''
                    for row in coor:
                        print(row)
                    '''
                    return x+round(level/2), y+round(level/2)
    return 9999, 9999
                
def text_mode_debug(img):
    # Create Label
    lst = [
        EAC, EAC, EAC, EAC, EAC,
        EAC, EAC, EAC, EAC, EAC,
        EAC, EAC, EAC, EAC, EAC,
    ]
    # Paste Label
    for i in lst:
        label_paste(img, i)

    # Print Result Picture
    # img.show()

    # Print Index
    print('-----index-----')
    for i in index:
        print(i)

def wr_text_on_img(text, img_path, pos):
    font = ImageFont.truetype("media/fontType/arial.ttf", 21)
    img = img2rgba(img_path)
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, (0, 0, 0), font=font)
    ImageDraw.Draw(img)
    return img

def power_rating2img(lines, ampere, is_china_only):
    pygame.init()
    china_dc_1_img = img2rgba("media/others/china_dc_1.png")
    china_dc_2_img = img2rgba("media/others/china_dc_2.png")
    font = pygame.font.Font("media/fontType/arial-unicode-ms.ttf", 21)
    line_num = lines.split('\r\n')
    ac_symbol = img2rgba('media/others/ac_symbol.png')
    ftext = font.render(ampere, True, (0, 0, 0),(255, 255, 255))
    pygame.image.save(ftext, "media/power_rating2img2_tmp.png")
    ampere_img = cut_img_top_bottom_10pixel(img2rgba("media/power_rating2img2_tmp.png"))
    ac_x_size, ac_y_size = ac_symbol.size
    ampere_x_size, ampere_y_size = ampere_img.size
    # print('ampere_x_size=', ampere_x_size)

    if len(line_num) == 1:
        img_line_1 = transfer_text2img(lines)
        line_1_x_size, line_1_y_size = img_line_1.size

        if is_china_only == True and ampere is not None:
            max_x_size = max(line_1_x_size+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = line_1_y_size+china_dc_1_img.size[1]+china_dc_2_img.size[1]
        elif is_china_only == True and ampere is None:
            max_x_size = max(line_1_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = line_1_y_size+china_dc_1_img.size[1]+china_dc_2_img.size[1]
        elif is_china_only == False and ampere is not None:
            max_x_size = line_1_x_size+ac_x_size+ampere_x_size
            max_y_size = line_1_y_size
        else:
            max_x_size = line_1_x_size
            max_y_size = line_1_y_size

        img = Image.new('RGBA', (max_x_size+14, max_y_size), (0, 0, 0, 0))
        img.paste(img_line_1, (5, 0))

        if ampere is not None:
            img.paste(ac_symbol, (5+line_1_x_size, 0))
            img.paste(ampere_img, (5+line_1_x_size+ac_x_size, 0))

        if is_china_only == True:
            img.paste(china_dc_1_img, (0, line_1_y_size))
            img.paste(china_dc_2_img, (0, line_1_y_size + china_dc_1_img.size[1]))

    elif len(line_num) == 2:
        lst_line = lines.split('\r\n')

        img_line_1 = transfer_text2img(lst_line[0])
        img_line_2 = transfer_text2img(lst_line[1])

        if is_china_only == True and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0]+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == True and ampere is None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == False and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0]+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1]
        else:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1]

        img = Image.new('RGBA', (max_x_size+10, max_y_size), (0, 0, 0, 0))
        img.paste(img_line_1, (5, 0))
        img.paste(img_line_2, (5, img_line_1.size[1]))

        if ampere is not None:
            img.paste(ac_symbol, (5+img_line_2.size[0], img_line_1.size[1]))
            img.paste(ampere_img, (5+img_line_2.size[0]+ac_x_size, img_line_1.size[1]))

        if is_china_only == True:
            img.paste(china_dc_1_img, (5, img_line_1.size[1]+img_line_2.size[1]))
            img.paste(china_dc_2_img, (5, img_line_1.size[1]+img_line_2.size[1]+china_dc_1_img.size[1]))

    elif len(line_num) == 3:
        lst_line = lines.split('\r\n')

        img_line_1 = transfer_text2img(lst_line[0])
        img_line_2 = transfer_text2img(lst_line[1])
        img_line_3 = transfer_text2img(lst_line[2])

        if is_china_only == True and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0]+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == True and ampere is None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == False and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0]+ac_x_size+ampere_x_size)
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1]
        else:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1]

        img = Image.new('RGBA', (max_x_size+10, max_y_size), (0, 0, 0, 0))
        img.paste(img_line_1, (5, 0))
        img.paste(img_line_2, (5, img_line_1.size[1]))
        img.paste(img_line_3, (5, img_line_1.size[1]+img_line_2.size[1]))

        if ampere is not None:
            img.paste(ac_symbol, (5+img_line_3.size[0], img_line_1.size[1]+img_line_2.size[1]))
            img.paste(ampere_img, (5+img_line_3.size[0]+ac_x_size, img_line_1.size[1]+img_line_2.size[1]))

        if is_china_only == True:
            img.paste(china_dc_1_img, (5, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]))
            img.paste(china_dc_2_img, (5, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]+china_dc_1_img.size[1]))

    elif len(line_num) == 4:
        lst_line = lines.split('\r\n')

        img_line_1 = transfer_text2img(lst_line[0])
        img_line_2 = transfer_text2img(lst_line[1])
        img_line_3 = transfer_text2img(lst_line[2])
        img_line_4 = transfer_text2img(lst_line[3])

        if is_china_only == True:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0]+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        else:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0]+ac_x_size+ampere_x_size)
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1]

        if is_china_only == True and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0]+ac_x_size+ampere_x_size, china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == True and ampere is None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0], china_dc_1_img.size[0], china_dc_2_img.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1] + china_dc_1_img.size[1] + china_dc_2_img.size[1]
        elif is_china_only == False and ampere is not None:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0]+ac_x_size+ampere_x_size)
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1]
        else:
            max_x_size = max(img_line_1.size[0], img_line_2.size[0], img_line_3.size[0], img_line_4.size[0])
            max_y_size = img_line_1.size[1] + img_line_2.size[1] + img_line_3.size[1] + img_line_4.size[1]

        img = Image.new('RGBA', (max_x_size+10, max_y_size), (0, 0, 0, 0))
        img.paste(img_line_1, (5, 0))
        img.paste(img_line_2, (5, img_line_1.size[1]))
        img.paste(img_line_3, (5, img_line_1.size[1]+img_line_2.size[1]))
        img.paste(img_line_4, (5, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]))

        if ampere is not None:
            img.paste(ac_symbol, (5+img_line_4.size[0], img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]))
            img.paste(ampere_img, (5+img_line_4.size[0]+ac_x_size, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]))

        if is_china_only == True:
            img.paste(china_dc_1_img, (5, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]+img_line_4.size[1]))
            img.paste(china_dc_2_img, (5, img_line_1.size[1]+img_line_2.size[1]+img_line_3.size[1]+img_line_4.size[1]+china_dc_1_img.size[1]))

    b_img = img2rgba('media/pure/black.png')
    b_img = b_img.resize((max_x_size+16, max_y_size+6))
    b_img.paste(img, (3, 3))
    b_img.save('media/power_rating2img_tmp.png')
    return b_img

def transfer_text2img(one_line):
    pygame.init()
    font = pygame.font.Font("media/fontType/arial-unicode-ms.ttf", 21)
    ftext = font.render(str(one_line), True, (0, 0, 0),(255, 255, 255))
    path = "media/transfer_text2img.png"
    pygame.image.save(ftext, path)
    img = img2rgba(path)
    img = cut_img_top_bottom_10pixel(img)
    return img

def cut_img_top_bottom_10pixel(img):
    # top cut 6 pixel
    # bottom cut 4 pixel
    new_img = Image.new('RGBA', (img.size[0], img.size[1]-10), (0, 0, 0, 0))
    new_img.paste(img, (0, -6))
    return new_img

def img_path_cal_area(img_path):
    img = img2rgba(img_path)
    return img.size[0]*img.size[1]
    

def snippet_detail(request):
    global coor

    sizes = LabelSize.objects.all()
    icons = Icon.objects.all()
    warnings = Warning.objects.all()
    madeins = MadeIn.objects.all()
    companylogos = CompanyLogo.objects.all()
    labels = Label.objects.all()
    areas = Area.objects.all()

    if request.method == 'POST':
        print(request.POST)
        
    return render(request, 'agency_label.html',locals())

def snippet_detail_backup(request):
    global coor

    sizes = LabelSize.objects.all()
    icons = Icon.objects.all()
    warnings = Warning.objects.all()
    madeins = MadeIn.objects.all()
    companylogos = CompanyLogo.objects.all()
    labels = Label.objects.all()
    areas = Area.objects.all()

    if request.method == 'POST':
        print(request.POST)
        
        part_no = request.POST['part_number']
        rule_model_name = request.POST['rule_model_name']
        model_name = request.POST['model_name']
        if request.POST.get('server') == None:
            server = False
        else:
            server = True
        power_rating_1 = request.POST['power_rating_1']
        power_rating_2 = request.POST['power_rating_2']
        
        
        '''
        Label.objects.create(
            part_no = part_no
            company = company,
            madein = madein,
            rule_model_name = rule_model_name,
            model_name = model_name,
            power_rating_1 = power_rating_1,
        )
        '''

        for size in sizes:
            if request.POST['dimension'] == size.category:
                base_img = img2rgba(size.img_path)
                base_img_x, base_img_y = base_img.size
                '''
                coor=[[0]*4 for i in range(6)] means below: 

                [0][1][2][3]
                [0, 0, 0, 0]    coor[0]
                [0, 0, 0, 0]    coor[1]
                [0, 0, 0, 0]    coor[2]
                [0, 0, 0, 0]    coor[3]
                [0, 0, 0, 0]    coor[4]
                [0, 0, 0, 0]    coor[5]

                coor[y][x]

                '''
                coor=[[0]*math.floor((base_img_x-30)/UNIT) for i in range(math.floor((base_img_y-20)/UNIT))]
        full_img = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        full_img.paste(base_img, (0, 0))


        global text_position_x, text_position_y, index
        text_position_x = 15
        text_position_y = 10
        index = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        
        for companylogo in companylogos:
            if request.POST['companylogo'] == companylogo.name:
                # text_paste(full_img, companylogo.img_path)
                if companylogo.name != "None":
                    all_paste(full_img, companylogo.img_path)
        '''
        all_paste(full_img, transfer_text2img("Server/服务器"))
        all_paste(full_img, transfer_text2img("制造商:英业达科技有限公司"))
        all_paste(full_img, transfer_text2img("Model/产品型号: Rattata"))
        all_paste(full_img, transfer_text2img("Input/额定输入:"))
        all_paste(full_img, transfer_text2img("生产地: 中国 Made in China"))
        '''

        for madein in madeins:
            if request.POST['madein'] == madein.name:
                # text_paste(full_img, madein.img_path)
                all_paste(full_img, madein.img_path)
                code_name = madein.code_name

        if rule_model_name != '':
            reg_mod_img = wr_text_on_img(rule_model_name, REGULATORY_MODEL_NUMBER, REG_MOD_NUM_TEXT_POS)
            reg_mod_img.save('media/tmp_reg_mod.png')
            # text_paste(full_img, 'media/tmp_reg_mod.png')
            all_paste(full_img, 'media/tmp_reg_mod.png')
        
        if server is True:
            # text_paste(full_img, 'media/others/Server.png')
            all_paste(full_img, 'media/others/Server.png')

        # text_paste(full_img, 'media/others/input.png')
        all_paste(full_img, 'media/others/input.png')
        
        tmp_path = power_rating2img(power_rating_1, power_rating_2, 0)
        if tmp_path:
            # text_paste(full_img, tmp_path)
            all_paste(full_img, tmp_path)
        
        # text_paste(full_img, 'media/others/for_each_inlet.png')
        all_paste(full_img, 'media/others/for_each_inlet.png')

        if model_name != '':
            mod_img = wr_text_on_img(model_name, MODEL_NUMBER, MOD_NUM_TEXT_POS)
            mod_img.save('media/tmp_mod.png')
            # text_paste(full_img, 'media/tmp_mod.png')
            all_paste(full_img, 'media/tmp_mod.png')
        

        str_tmp = part_no + "   " + code_name + "   "
        
        transfer_text2img(str_tmp)
        
        all_paste(full_img, "media/part_no_madein_tmp.png")
        
        
        '''
        for icon in icons:
            if request.POST['icon'] == icon.name:
                all_paste_icon(full_img, icon.img_path)

        for warning in warnings:
            if request.POST['warning'] == warning.name:
                all_paste(full_img, warning.img_path)
        '''

        all_paste(full_img, 'media\Warnings\Warning_EMC_02.png')
        # all_paste(full_img, 'media\Warnings\FCC_capital.png')
        all_paste(full_img, 'media\Warnings\Warning_All power off_Simplified Chinese.png')
        all_paste(full_img, 'media\Warnings\Warning_disconnetc power_02.png')
        

        '''
        for i in range(3):
            # all_paste_icon(full_img, 'media\Icons\6-Battery_AI_30x30mm_Artboard_PS.jpg')
            # all_paste_icon(full_img, 'media\Icons\7-CE_HPE_AI_40x30mm_Artboard_PS.jpg')
            all_paste_icon(full_img, 'media\Icons\America-UL-E149282_HPE_30x30mm.png')
            all_paste_icon(full_img, 'media\Icons\China-CCC_30x20mm.png')
            all_paste(full_img, 'media\Icons\India_BIS_HPE_IPT_20x20mm.png')
        '''

        # all_paste_icon(full_img, "media/tmp/9.jpg")
        all_paste_icon(full_img, "media/tmp/18.png")
        all_paste_icon(full_img, "media/tmp/11.jpg")
        all_paste_icon(full_img, "media/tmp/17.png")
        # all_paste_icon(full_img, "media/tmp/19.png")


        # text_mode_debug(full_img)

        # barcode_img = img2rgba("media/others/barcode_0422.png")
        # full_img.paste(barcode_img, (BARCODE_X, BARCODE_Y))
        
        # full_img = resize_img_80_percent(full_img)

        img_name = str(uuid.uuid4())
        img_url = 'media/'+img_name+'.png'

        full_img.convert('RGB').save(img_url)
        """
        return render(request, 'agency_label.html', 
            {
                'img_url': img_url,
                'object_label'
            }
        )
        """
        return render(request, 'agency_label.html',locals())
    else:
        return render(request, 'agency_label.html',locals())
        # return render(request, 'agency_label.html')


def golden_sample(request):
    sizes = LabelSize.objects.all()
    icons = Icon.objects.all()
    warnings = Warning.objects.all()
    madeins = MadeIn.objects.all()
    companylogos = CompanyLogo.objects.all()
    labels = Label.objects.all()
    areas = Area.objects.all()

    # print("func to filter forign Key ", Area.objects.filter(part_no=Label.objects.get(part_no = '1810B0258701')))
    # use __ connect to forign Key
    # print("Area.objects.filter(part_no__part_no='1810B0258701') = ", Area.objects.filter(part_no__part_no='1810B0258701'))

    if request.method == 'POST':
        part_no = request.POST['part_no']

        size = LabelSize.objects.get(category = Label.objects.get(part_no=part_no).label_size)
        base_img = img2rgba(size.img_path)

        label_img = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        label_img.paste(base_img, (0, 0))

        for area in Area.objects.filter(part_no__part_no=part_no):
            pattern = re.compile(r'\d+')
            x1 = int(pattern.findall(area.area_coor)[0])
            y1 = int(pattern.findall(area.area_coor)[1])
            x2 = int(pattern.findall(area.area_coor)[2])
            y2 = int(pattern.findall(area.area_coor)[3])
            y_index = 0

            area_img = Image.new('RGBA', (x2-x1, y2-y1), (0, 0, 0, 0))

            if area.company is not None:
                company = companylogos.get(name = area.company.name)
                company_img = img2rgba(company.img_path)
                area_img.paste(company_img, (0, y_index))
                y_index += company_img.size[1]

            if area.rule_model_name is not None:
                reg_mod_img = wr_text_on_img(area.rule_model_name, REGULATORY_MODEL_NUMBER, REG_MOD_NUM_TEXT_POS)
                area_img.paste(reg_mod_img,(0,y_index))
                y_index += reg_mod_img.size[1]

            madein = MadeIn.objects.get(name = Label.objects.get(part_no=part_no).madein)
            # print(type(madein))
            # print(madein.code_name)

            if area.madein_show == True:
                madein_img = img2rgba(madein.img_path)
                area_img.paste(madein_img, (0, y_index))
                y_index += madein_img.size[1]

            if area.madein_code_show == True:
                madein_code_img = transfer_text2img(madein.code_name)
                area_img.paste(madein_code_img, (0, y_index))
                y_index += madein_code_img.size[1]
            
            '''
            if area.madein is not None:
                madein = madeins.get(name = area.madein.name)
                if area.madein_show == True:
                    madein_code_img = transfer_text2img(madein.code_name)
                    area_img.paste(madein_code_img, (0, y_index))
                    y_index += madein_code_img.size[1]
                else:
                    madein_img = img2rgba(madein.img_path)
                    area_img.paste(madein_img, (0, y_index))
                    y_index += madein_img.size[1]
            '''

            for warning in area.warnings.all():
                warning_img = img2rgba(warning.img_path)
                area_img.paste(warning_img, (0, y_index))
                y_index += warning_img.size[1]

            if area.server == True:
                server_img = img2rgba('media/others/Server.png')
                area_img.paste(server_img, (0, y_index))
                y_index += server_img.size[1]

            if area.power_rating_1 != "":
                input_img = img2rgba('media/others/input.png')
                area_img.paste(input_img, (0, y_index))
                y_index += input_img.size[1]
                power_rating_img = power_rating2img(area.power_rating_1, area.power_rating_2, area.china_only)
                area_img.paste(power_rating_img, (0, y_index))
                y_index += power_rating_img.size[1]
                for_each_inlet_img = img2rgba('media/others/for_each_inlet.png')
                area_img.paste(for_each_inlet_img, (0, y_index))
                y_index += for_each_inlet_img.size[1]

            if area.model_name is not None:
                '''
                mod_img = wr_text_on_img(area.model_name, MODEL_NUMBER, MOD_NUM_TEXT_POS)
                area_img.paste(mod_img,(0,y_index))
                y_index += mod_img.size[1]
                '''
                mod_img_1 = img2rgba(MODEL_NUMBER)
                area_img.paste(mod_img_1,(0,y_index))
                y_index += mod_img_1.size[1]
                
                mod_img_2 = transfer_text2img(area.model_name)
                area_img.paste(mod_img_2,(0,y_index))
                y_index += mod_img_2.size[1]

            if area.icons.all().exists():
                coor = []
                icon_size = 0
                area_size = (x2-x1)*(y2-y1)
                coor=[[0]*math.floor((x2-x1)/UNIT) for i in range(math.floor((y2-y1)/UNIT))]

                icon_lst = []

                for icon in area.icons.all():
                    # print(f"icon.img_path type = {type(icon.img_path)}")
                    # print(f"icon.img_path = {icon.img_path}")
                    icon_img = img2rgba(icon.img_path)
                    icon_img = resize_img(icon_img, ICON_SHRINK_PERCENT)
                    icon_size += icon_img.size[0]*icon_img.size[1]
                    icon_lst.append(str(icon.img_path))
                
                if icon_size/area_size <= 0.1:
                    level = 14
                elif icon_size/area_size <= 0.2:
                    level = 9
                elif icon_size/area_size <= 0.3:
                    level = 5
                elif icon_size/area_size <= 0.4:
                    level = 3
                else:
                    level = 2
                
                print(f"\nlevel = {level} \n")

                icon_lst_sort = sorted(icon_lst, key = lambda x:img_path_cal_area('media/'+x), reverse=True)

                for icon in icon_lst_sort:
                    icon_img = img2rgba('media/'+icon)
                    icon_img = resize_img(icon_img, ICON_SHRINK_PERCENT)
                    if all_paste(area_img, icon_img, coor, level) == 0:
                        print("\nNo space for", icon,"\n")

                # print(area.name)
                # print("level = ",level)
                # print("area size = ",area_size)
                # print("icon size = ", icon_size)

                '''
                if area.icons.all().exists():
                    print("level = ",level)
                    for icon in area.icons.all():
                        icon_img = img2rgba(icon.img_path)
                        icon_img = resize_img(icon_img, ICON_SHRINK_PERCENT)
                        if all_paste(area_img, icon_img, coor, level) == 0:
                            print("\nNo space for", icon.name,"\n")
                '''

            if area.part_no_show == True:
                part_no_img = transfer_text2img(area.part_no)
                area_img.paste(part_no_img, (0, y_index))
                y_index += part_no_img.size[1]

            label_img.paste(area_img, (x1, y1))
            img_url = 'media/'+ str(part_no) +'.png'
            label_img.save(img_url, dpi=(300, 300))

        return render(request, 'golden_sample.html',locals(),)
    return render(request, 'golden_sample.html',locals())

def upload_img(request):
    if request.method == 'POST':
        icon_img = request.FILES['icon_img']
        
        fs = FileSystemStorage()
        filename = fs.save('Icons\\'+icon_img.name, icon_img)
        Icon.objects.create(
            name = request.POST['icon_name'],
            img_path = 'Icons\\'+icon_img.name,
        )
        warning_img = request.FILES['warning_img']
        
        fs = FileSystemStorage()
        filename = fs.save('Warnings\\'+warning_img.name, warning_img)
        Warning.objects.create(
            name = request.POST['warning_name'],
            img_path = 'Warnings\\'+warning_img.name,
        )

        
    return render(request, 'upload_img.html', locals())

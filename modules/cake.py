import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import re


class Cake(object):
    def __init__(self, txtsrc):
        self.bline = 70
        self.bline_text = 80
        self.width = 2480
        self.imgarray = [header(self.width)]
        self.txt = self.fromtxt(txtsrc)
        self.cake = None

    def fromtxt(self, txtsrc):
        with open('./resources/'+txtsrc, 'r', encoding='utf-8') as F:
            txt = F.read()
        return txt.split('\n')

    def render(self):
        for element in self.txt:
            self.imgarray.append(self.template(element))
        self.imgarray.append(botton(self.width))
        self.cake = cv2.vconcat(self.imgarray)

    def template(self, element):

        if element[0:3] == '###':
            title = np.zeros((188, self.width, 3), np.uint8)
            title.fill(208)
            cv2.rectangle(title, (self.bline, 0),
                          (self.width-self.bline, 140), (48, 48, 48), -1)

            title_text = element[3:]
            title = writeText(title, '<b>'+title_text+'</b>',
                              (self.bline_text, 50), 50, (255, 255, 255))
            return title

        elif element[0:3] == '{{{':
            _img = cv2.imread(
                './resources/'+element[3:], flags=cv2.IMREAD_COLOR)
            _img = cv2.resize(_img, (2340, int(_img.shape[0]*2340/_img.shape[1])))
            img = np.zeros((50 + 25 + _img.shape[0], self.width, 3), np.uint8)
            img.fill(208)
            img = imgpast(img, _img, 70, 50)
            return img

        elif element == '<br>':
            br = np.zeros((50, self.width, 3), np.uint8)
            br.fill(208)
            return br
        else:
            p_text = p_linesinsert(element)
            p = np.zeros((64 + relen(re.search('\n', p_text))
                         * 41, self.width, 3), np.uint8)
            p.fill(208)
            p = writeText(p, p_text, (self.bline_text, 0), 37)
            return p


def textbreak(txt):
    i = txt
    arr = []
    pointer = True
    while pointer:
        _b = re.search('<b>[\s\S]*?<\/b>', i)
        if _b != None:
            _b = _b.regs[0]
        else:
            _b = (999999, 999999)
        _l = re.search('<l>[\s\S]*?<\/l>', i)
        if _l != None:
            _l = _l.regs[0]
        else:
            _l = (999999, 999999)
        if _b[0] != 0 and _l[0] != 0 and i != "":
            _n = re.search('\n', i[0:min(_b[0], _l[0])])
            if _n != None:
                _arr = i[0:min(_b[0], _l[0])].replace(
                    '\n', '<%\n<%').split('<%')
                for ii in range(0, len(_arr)):
                    if _arr[ii] == '\n':
                        _arr[ii] = ['\n', 'n']
                    else:
                        _arr[ii] = [_arr[ii], 'p']
                arr.extend(_arr)
            else:
                arr.append([i[0:min(_b[0], _l[0])], 'p'])
            i = i[min(_b[0], _l[0]):]
        elif _l[0] == 0:
            _n = re.search('\n', i[_l[0]:_l[1]])
            if _n != None:
                _arr = i[_l[0]:_l[1]].replace('\n', '<%\n<%').split('<%')
                for ii in range(0, len(_arr)):
                    if _arr[ii] == '\n':
                        _arr[ii] = ['\n', 'n']
                    else:
                        _arr[ii] = [_arr[ii].replace(
                            '<l>', '').replace('</l>', ''), 'l']
                arr.extend(_arr)
            else:
                arr.append([i[_l[0]:_l[1]].replace(
                    '<l>', '').replace('</l>', ''), 'l'])
            i = i[_l[1]:]
        elif _b[0] == 0:
            _n = re.search('\n', i[_b[0]:_b[1]])
            if _n != None:
                _arr = i[_b[0]:_b[1]].replace('\n', '<%\n<%').split('<%')
                for ii in range(0, len(_arr)):
                    if _arr[ii] == '\n':
                        _arr[ii] = ['\n', 'n']
                    else:
                        _arr[ii] = [_arr[ii].replace(
                            '<b>', '').replace('</b>', ''), 'b']
                arr.extend(_arr)
            else:
                arr.append([i[_b[0]:_b[1]].replace(
                    '<b>', '').replace('</b>', ''), 'b'])
            i = i[_b[1]:]
        elif i == "":
            pointer = False

    return colorrender(arr)


def colorrender(arr):
    newarr = []
    for iandw in arr:
        i = iandw[0]
        colorStart = re.search('<\/(red|white|black)>', i)
        colorEnd = re.search('<(red|white|black)>', i)
        if colorStart != None:
            color = colorStart[1].replace('<', '').replace('>', '')
            colorStart = colorStart.regs[0]
            _colorStart = re.search('<(red|white|black)>', i[:colorStart[0]])
            if _colorStart == None:
                i = '<' + color+'>' + i
        if colorEnd != None:
            color = colorEnd.group(1).replace('</', '').replace('>', '')
            colorEnd = colorEnd.regs[-1]
            _colorEnd = re.search('<\/(red|white|black)>', i[colorEnd[1]:])
            if _colorEnd == None:
                i = i + '</' + color + '>'
        pointer = True
        _newarr = []
        while pointer:
            colorFull = re.search(
                '<(red|white|black)>[\s\S]*<\/(red|white|black)>', i)
            if colorFull != None:
                colorFull = colorFull.regs[0]
            else:
                colorFull = (999999, 999999)
            if colorFull[0] != 0 and i != '':
                _newarr.append([i[:colorFull[0]], iandw[1], 'black'])
                i = i[colorFull[0]:]
            elif colorFull[0] == 0:
                _color = re.search('<(red|white|black)>', i)[
                    0].replace('<', '').replace('>', '')
                _newarr.append([i[colorFull[0]:colorFull[1]].replace(
                    '<'+_color+'>', '').replace('</'+_color+'>', ''), iandw[1], _color])
                i = i[colorFull[1]:]
            elif i == '':
                pointer = False
        newarr.extend(_newarr)
    return newarr


def writeText(img, _txt, position, size, color=None):
    mapper = {"l": "Light",
              "p": "Regular",
              "b": "Bold",
              "red": (197, 40, 30),
              "white": (255, 255, 255),
              "black": (0, 0, 0)
              }
    txt = textbreak(_txt)
    img_PIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_PIL)
    px = (0, position[1], position[0], 0)
    for words in txt:
        _color = None
        if words[1] == 'n':
            px = (0, px[1]+(size*1.15), position[0], 0)
        else:
            if color:
                _color = color
            else:
                _color = mapper[words[2]]
            font = ImageFont.truetype(
                './fonts/SourceHanSansCN-' + mapper[words[1]] + '.otf', size)
            draw.text(((px[2], px[1])), words[0],
                      fill=_color, font=font, spacing=size*0.4)
            px = draw.textbbox((px[2], px[1]), words[0],
                               font=font, spacing=size*0.4)
    img_cv2 = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
    return img_cv2


def imgpast(imgfrom, imgto, startx, starty):
    y = imgto.shape[0]
    x = imgto.shape[1]

    imgfrom[starty:starty+y, startx:startx+x] = imgto
    return imgfrom


def relen(a):
    if a == None:
        return 0
    else:
        m = a.regs
        return len(a.regs)


def p_linesinsert(element):
    if len(element) <= 3:
        return element
    counter = 0
    counter_2 = 0
    while counter <= len(element):
        i = element[counter:]
        i_re = re.search(
            '<(l|b|p|red|black|white)>|<\/(l|b|p|red|black|white)>', i)
        if i_re != None:
            if i_re.regs[0][0] == 0:
                counter = counter+i_re.regs[0][1]-i_re.regs[0][0]
            else:
                counter = counter+1
                if re.search('[A-Za-z0-9_\-~!@#$%\^\+\*&\\\/\?\|:\.<>{}()\'\;\="]', element[counter-1:counter]) != None:
                    counter_2 = counter_2+1
                else:
                    counter_2 = counter_2+2
        else:
            counter = counter+1
            if re.search('[A-Za-z0-9_\-~!@#$%\^\+\*&\\\/\?\|:\.<>{}()\'\;\="]', element[counter-1:counter]) != None:
                counter_2 = counter_2+1
            else:
                counter_2 = counter_2+2
        if counter_2 >= 121:
            element = element[:counter]+'\n'+element[counter:]
            counter_2 = 0
            counter = counter+1
    return element


def header(width):
    a = np.zeros((70, width, 3), np.uint8)
    a.fill(208)
    return a


def botton(width):
    img = np.zeros((250, width, 3), np.uint8)
    img.fill(208)
    time_cc = time.localtime(time.time())
    txt = '罗德岛蜜饼工坊\n'+str(time_cc.tm_year).zfill(2) + '年'+str(
        time_cc.tm_mon).zfill(2) + '月' + str(time_cc.tm_mday).zfill(2) + '日'
    img_PIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_PIL)
    font = ImageFont.truetype(
        './fonts/SourceHanSansCN-Regular.otf', 37)
    px = draw.textbbox((0, 0), txt, font=font, spacing=5, align='right')
    draw.text((width-px[2]+px[0]-80, 110), txt,
              fill=(0, 0, 0), font=font, spacing=5, align='right')
    img_cv2 = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

    return img_cv2
# cake = Cake('./resources/index.txt')

from PIL import Image, ImageDraw, ImageFont
from random import choice, sample
from math import floor
from os import walk, remove, path, mkdir
from datetime import datetime, timedelta

class idioms_game:
    def __init__(self):
        # Load data
        self.data = []
        with open(path.join(path.dirname(path.realpath(__file__)),'data.txt'), encoding='utf-8', mode='r') as f:
            self.data = f.readlines()

    require_image = True

    def clean(self):
        try:
            for dirpath, dirnames, filenames in walk(path.join(path.dirname(path.realpath(__file__)),'temp')):
                for file in filenames:
                    if not '.png' in file:
                        continue
                    curpath = path.join(dirpath, file)
                    file_modified = datetime.fromtimestamp(path.getmtime(curpath))
                    if datetime.now() - file_modified > timedelta(minutes=5):
                        remove(curpath)
        except OSError:
            pass

    def generate(self, identifier):
        save_path = path.join(path.dirname(path.realpath(__file__)),'temp')
        try:
            if not(path.exists(save_path)):
                mkdir(save_path)
        except OSError:
            return {
                'error_message': '无法建立临时文件夹',
                }

        # Base image
        w = 480
        h = int(w / 4)
        img = Image.new('RGB', (w, h), color = (255, 255, 255))
        img_hint = Image.new('RGB', (w, h), color = (255, 255, 255))

        try:
            font = ImageFont.truetype('simkai.ttf', h)
        except:
            return {
                'error_message': '找不到所需字体文件simkai.ttf',
                }            

        draw = ImageDraw.Draw(img)
        draw_hint = ImageDraw.Draw(img_hint)

        answer = choice(self.data).strip()

        draw.text((0,0), f'{answer}', font=font, fill=(0, 0, 0))
        draw_hint.text((0,0), f'{answer}', font=font, fill=(0, 0, 0))

        image_name = f'{datetime.now():%Y%m%d-%H%M%S}_{identifier}'
        img.save(f'{path.join(save_path, image_name)}.png', 'PNG')

        # Mask settings
        mask_col = 3
        mask_row = 3
        reveal_blocks = 2
        hint_reveal_blocks = 1
        block_fill = (200, 200, 200)
        grid_fill = (128, 128, 128)
        grid_width = 3

        # Rectangles
        reveal_blocks = min((mask_col * mask_row, reveal_blocks))
        if hint_reveal_blocks + reveal_blocks > mask_col * mask_row:
            hint_reveal_blocks = 0
        for character in range(0, 4):
            mask = [0] * mask_col * mask_row
            for i in sample(range(0, mask_col * mask_row), reveal_blocks):
                mask[i] = 1
            for row in range(0, mask_row):
                for col in range(0, mask_col):
                    if mask[row * mask_col + col] == 0:
                        draw.rectangle((h * character + col * h / mask_col, row * h / mask_row, h * character + (col+1) * h / mask_col, (row+1) * h / mask_row), fill=block_fill)
            if hint_reveal_blocks > 0:
                mask_hint = mask
                hint = [i for i, j in enumerate(mask) if j == 0]
                for i in sample(hint, k=hint_reveal_blocks):
                    mask_hint[i] = 1
                for row in range(0, mask_row):
                    for col in range(0, mask_col):
                        if mask_hint[row * mask_col + col] == 0:
                            draw_hint.rectangle((h * character + col * h / mask_col, row * h / mask_row, h * character + (col+1) * h / mask_col, (row+1) * h / mask_row), fill=block_fill)

        # Mask grid
        for i in range(1, mask_row):
            draw.line((0, int(h / mask_row) * i - floor(grid_width / 2), w, int(h / mask_row) * i - floor(grid_width / 2)), fill=grid_fill, width=grid_width)

        for i in range(1, mask_col * 4):
            draw.line((int(w / mask_col / 4) * i - floor(grid_width / 2), 0, int(w / mask_col / 4) * i - floor(grid_width / 2), h), fill=grid_fill, width=grid_width)

        for i in range(1, mask_row):
            draw_hint.line((0, int(h / mask_row) * i - floor(grid_width / 2), w, int(h / mask_row) * i - floor(grid_width / 2)), fill=grid_fill, width=grid_width)

        for i in range(1, mask_col * 4):
            draw_hint.line((int(w / mask_col / 4) * i - floor(grid_width / 2), 0, int(w / mask_col / 4) * i - floor(grid_width / 2), h), fill=grid_fill, width=grid_width)

        img.save(f'{path.join(save_path, image_name)}_masked.png', 'PNG')
        if hint_reveal_blocks > 0:
            img_hint.save(f'{path.join(save_path, image_name)}_hint.png', 'PNG')

        result = {
            'question': f'请写出以下成语或熟语：[CQ:image,file=file:///{path.join(save_path, image_name)}_masked.png]',
            'answer': f'{answer}',
            'answer_announce': f'回答正确！答案是：{answer}',
            'hint': f'提示：[CQ:image,file=file:///{path.join(save_path, image_name)}_hint.png]' if hint_reveal_blocks > 0 else '',
        }

        return result

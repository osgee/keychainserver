from PIL import Image, ImageDraw, ImageFont
import random


def getcaptcha():
	base = ('0','1','2','3','4','5','6','7','8','9',  
			'A','B','C','D','E','F','G','H','I','J',  
			'K','L','M','N','O','P','Q','R','S','T',  
			'U','V','W','X','Y','Z')

	imglen = 4
	footimg = Image.open('keychain/font_t.png')
	captcha = Image.new('RGBA', (19*imglen, 25))
	code = ''
	for x in range(imglen):
		ran = random.randint(0,35)
		code = ''.join((code, base[ran]))
		img_s = footimg.crop((ran*19, 0, (ran+1)*19, 20))
		img_s = img_s.rotate(random.randint(-30, 30))
		captcha.paste(img_s, (x*19, 2))
	return captcha, code
import requests
from bs4 import BeautifulSoup
import time
from telebot import TeleBot
import csv
import threading
import datetime
from secrets import TELEGRAM_TOKEN
import zipfile
import os
from telebot import apihelper
from lxml import etree
from lxml import html
import datetime
import shutil
import calendar
import re

# apihelper.proxy = {'https':'https://47.56.4.34:80'}
chat_ids = []
URL = 'https://www.bilauppbod.is'
thumb_identify = ''

app = TeleBot(TELEGRAM_TOKEN)


@app.message_handler(commands=['start'])
def example_command(message):
	geted_id = message.from_user.id
	with open('telegram.txt', 'r', encoding='utf-8') as f:
		ids_list = f.read().split(',')
		ids = ids_list
	if str(geted_id) not in ids:
		ids.append(str(geted_id))
		with open('telegram.txt', 'a') as f:
			f.write(f'{str(geted_id)},')
	msg = '''
		Здравствуйте!\nТеперь вам будут присылаться новые объявления с сайта bilauppbod.is
	'''
	app.send_message(geted_id, msg)

def main():
	global thumb_identify
	html = requests.get(URL).text
	soup = BeautifulSoup(html, 'html')
	post = soup.find_all("div", {"class": "auctionitem"})[-1]
	identify_url = post.find('a', {'class': 'thumbnail'}).attrs['href']
	# if not thumb_identify:
	# 	thumb_identify = identify_url
	if thumb_identify != identify_url:
		thumb_identify = identify_url
		print('new post')
		with open('telegram.txt', 'r') as f:
			ids_list = f.read().split(',')
			post_url = URL + post.find('h3').find('a').attrs['href']
			post_details = requests.get(post_url).text
			post_details_soup = BeautifulSoup(post_details, 'html')
			post_details_url = post_details_soup.find('div', {'id': 'auction_images'}).find_all('a')[0].attrs['href']
			# build text message
			table_rows = post_details_soup.find_all('tr')
			header = post.find('h3').find('a').text.strip()
			mileage = f"Пробег (км / мил):   {table_rows[10].find_all('td')[-1].text.strip()}"
			engine = f"Двигатель:   {table_rows[11].find_all('td')[-1].text.strip()}, объём {table_rows[12].find_all('td')[-1].text.strip()}"
			transmission = f"Коробка:   {table_rows[8].find_all('td')[-1].text.strip()}"
			registration = f"Дата первой регистрации:   {table_rows[5].find_all('td')[-1].text.strip()}"
			auction_date = f"Дата аукциона:   {post_details_soup.find('div', {'id': 'auction_bid'}).find('div', {'class': 'top'}).find_all('dd')[-1].text.strip()}"
			text = f"{header}\n\n{mileage}\n{engine}\n{transmission}\n{registration}\n{auction_date}"
			image_url = URL + post.find('img').attrs['src']
			image = requests.get(URL + post_details_url).content
			os.mkdir(header)
			with open(f'./{header}/'+header+'.png', 'wb') as f:
				f.write(image)
			with open(f'./{header}/'+header+'.txt', 'w') as f:
				f.write(text)
			shutil.make_archive(header, 'zip', header)
			shutil.rmtree(f'{header}/')
			# with open(header+'.zip', 'rb') as zipObj:
			for chat_id in ids_list:
				try:
					app.send_document(chat_id, open(header+'.zip','rb'))
					print(chat_id)
				except:
					pass	
			os.remove(header+'.zip')
	print('checkout ------- '+ post.find('h3').find('a').text.strip() +' -------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

def parse_week(soup):
	# td_href = soup.find('a', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionLink'}).attrs['href']
	# details_soup = BeautifulSoup(requests.get('http://utbod.vis.is/'+td_href).text, 'html')
	# table = details_soup.find('table', {'id': 'carTable'})
	# tr_list = table.find_all('tr')
	time_now = '2021-05-10'
	# os.mkdir(time_now)
	# for tr in tr_list[1:]:
	# 	tr_url = tr.find_all('td')[0].find('a').attrs['href']
	# 	table_details = requests.get('http://utbod.vis.is'+tr_url[2:])
	# 	tree = html.fromstring(table_details.content)
	# 	try:
	# 		astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/text()')[0]
	# 	except IndexError:
	# 		astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/font/text()')[0]
	# 	car_name = tree.xpath('//*[@id="MainPage__ctl3_nameofItem"]/text()')[0]
	# 	car_text = f'''\n
	# 	{car_name}
	# 	Útboðsnr.: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_number"]/text()')[0]}
	# 	Nýskráður: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_RegDate"]/text()')[0]}
	# 	Vélarstærð: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_EngineSize"]/text()')[0]}
	# 	Drif: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Drive"]/text()')[0]}
	# 	Litur: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Color"]/text()')[0]}
	# 	Í einkaeign: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_lablePrivateOwned"]/text()')[0]}
	# 	Ökutækjafl.: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_CarCategory"]/text()')[0]}
	# 	Staðsetning: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Location"]/text()')[0]}
	# 	Fastanúmer:	{tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_RegNumber"]/text()')[0]}
	# 	Ekinn: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Driven"]/text()')[0]}
	# 	Gírar: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Gears"]/text()')[0]}
	# 	Hurðir: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Doors"]/text()')[0]}
	# 	Eldsneyti: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_GasType"]/text()')[0]}
	# 	Ástand: {astand}
	# 	'''
	# 	soup_car = BeautifulSoup(table_details.content, 'html')
	# 	images_list = re.findall(r"(/items/ImageRenderer.*?)'", table_details.text)
	# 	for img_path in range(len(images_list)):
	# 		images_list[img_path] = images_list[img_path].replace('thumb', 'large')
	# 		img = requests.get('http://utbod.vis.is'+images_list[img_path]).content
	# 		with open(f'{time_now}/{car_name}-{img_path}.png', 'wb') as f:
	# 			f.write(img)

	# 	with open(f'{time_now}/{car_name}.txt', 'w') as f:
	# 		f.write(car_text)
	shutil.make_archive(time_now, 'zip', time_now)
	with open('telegram.txt', 'r') as f:
		ids_list = f.read().split(',')
		# with open(time_now+'.zip', 'rb') as zipObj:
		for chat_id in ids_list:
			try:
				app.send_document(chat_id, open(time_now+'.zip','rb'))
				print(chat_id)
			except:
				pass
	# shutil.rmtree(f'{time_now}/')
	os.remove(time_now+'.zip')
		
def bot_thread():
	print('### START TELEGRAM ###')
	app.polling()

def parser_thread():
	print('### START PARSER ###')
	flag_week = False
	old_name = ''
	while True:
		try:
			main()
		except: 
			pass
		req = requests.get('http://utbod.vis.is/default.aspx').text
		soup = BeautifulSoup(req, 'html')
		name = 's'
		try:
			name = soup.find('span', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionTitle'}).text.strip()
		except:
			print('auction not found')
		# try:
		if name is not old_name:
			parse_week(soup)
			old_name = name
		# except:
		# 	print('sth went wrong in parse_week()')
		time.sleep(120)

if __name__ == '__main__':
	thr_bot = threading.Thread(target=bot_thread)
	thr_bot.start()
	thr_parser = threading.Thread(target=parser_thread)
	thr_parser.start()
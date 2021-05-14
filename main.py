import requests
from bs4 import BeautifulSoup
import time
from telebot import TeleBot
import threading
import datetime
from secrets import TELEGRAM_TOKEN
import os
import datetime
import shutil
from lxml import html
import re

chat_ids = []
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

def first_parser():
	URL = 'https://www.bilauppbod.is'
	global thumb_identify
	html = requests.get(URL).text
	soup = BeautifulSoup(html, 'html')
	post = soup.find_all("div", {"class": "auctionitem"})[-1]
	identify_url = post.find('a', {'class': 'thumbnail'}).attrs['href']
	# if not thumb_identify:
	# 	thumb_identify = identify_url
	if thumb_identify != identify_url:
		thumb_identify = identify_url
		post_url = URL + post.find('h3').find('a').attrs['href']
		post_details = requests.get(post_url).text
		post_details_soup = BeautifulSoup(post_details, 'html')
		# post_details_url = post_details_soup.find('div', {'id': 'auction_images'}).find_all('a')[0].attrs['href']
		# build text message
		table_rows = post_details_soup.find_all('tr')
		header = post.find('h3').find('a').text.strip()
		mileage = f"Пробег (км / мил):   {table_rows[10].find_all('td')[-1].text.strip()}"
		engine = f"Двигатель:   {table_rows[11].find_all('td')[-1].text.strip()}, объём {table_rows[12].find_all('td')[-1].text.strip()}"
		transmission = f"Коробка:   {table_rows[8].find_all('td')[-1].text.strip()}"
		registration = f"Дата первой регистрации:   {table_rows[5].find_all('td')[-1].text.strip()}"
		auction_date = f"Дата аукциона:   {post_details_soup.find('div', {'id': 'auction_bid'}).find('div', {'class': 'top'}).find_all('dd')[-1].text.strip()}"
		text = f"{header}\n\n{mileage}\n{engine}\n{transmission}\n{registration}\n{auction_date}"
		images_url = post_details_soup.find_all('a', {'class': 'thumbnail'})
		files_name = 'bilauppbod ' + header
		os.mkdir(files_name)
		for url in range(len(images_url)):
			image = requests.get(URL + images_url[url].find('img').attrs['src'].split('_thumb')[0]+'.jpg').content
			with open(f'./{files_name}/'+str(url)+'.jpg', 'wb') as f:
				f.write(image)
		with open(f'./{files_name}/'+files_name+'.txt', 'w') as f:
			f.write(text)
		shutil.make_archive(files_name, 'zip', files_name)
		with open('telegram.txt', 'r') as f:
			ids_list = f.read().split(',')
			for chat_id in ids_list:
				try:
					app.send_document(chat_id, open(files_name+'.zip','rb'))
					# print(chat_id)
				except:
					pass	
		os.remove(files_name+'.zip')
		shutil.rmtree(f'{files_name}/')

def second_parser(soup):
	td_href = soup.find('a', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionLink'}).attrs['href']
	details_soup = BeautifulSoup(requests.get('http://utbod.vis.is/'+td_href).text, 'html')
	table = details_soup.find('table', {'id': 'carTable'})
	tr_list = table.find_all('tr')
	# time_now = str(datetime.datetime.today().strftime('%Y-%m-%d'))
	for tr in tr_list[1:]:
		tr_url = tr.find_all('td')[0].find('a').attrs['href']
		table_details = requests.get('http://utbod.vis.is'+tr_url[2:])
		tree = html.fromstring(table_details.content)
		try:
			astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/text()')[0]
		except IndexError:
			astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/font/text()')[0]
		car_name = tree.xpath('//*[@id="MainPage__ctl3_nameofItem"]/text()')[0]
		car_text = f'''\n
		{car_name}
		Útboðsnr.: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_number"]/text()')[0]}
		Nýskráður: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_RegDate"]/text()')[0]}
		Vélarstærð: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_EngineSize"]/text()')[0]}
		Drif: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Drive"]/text()')[0]}
		Litur: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Color"]/text()')[0]}
		Í einkaeign: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_lablePrivateOwned"]/text()')[0]}
		Ökutækjafl.: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_CarCategory"]/text()')[0]}
		Staðsetning: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Location"]/text()')[0]}
		Fastanúmer:	{tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_RegNumber"]/text()')[0]}
		Ekinn: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Driven"]/text()')[0]}
		Gírar: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Gears"]/text()')[0]}
		Hurðir: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Doors"]/text()')[0]}
		Eldsneyti: {tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_GasType"]/text()')[0]}
		Ástand: {astand}
		'''
		images_list = re.findall(r"(/items/ImageRenderer.*?)'", table_details.text)

		with open('telegram.txt', 'r') as f:
			ids_list = f.read().split(',')
			car_name = f'utbod - {car_name}'
			os.mkdir(car_name)
			for img_path in range(len(images_list)):
				images_list[img_path] = images_list[img_path].replace('thumb', 'large')
				img = requests.get('http://utbod.vis.is'+images_list[img_path]).content
				with open(f'{car_name}/{car_name}-{img_path}.png', 'wb') as f:
					f.write(img)
				with open(f'{car_name}/{car_name}.txt', 'w') as f:
					f.write(car_text)
			shutil.make_archive(car_name, 'zip', car_name)
			shutil.rmtree(f'{car_name}/')
			for chat_id in ids_list:
				try:
					app.send_document(chat_id, open(car_name+'.zip','rb'))
					# print(f'{car_name} - {chat_id}')
				except:
					pass
			os.remove(car_name+'.zip')
		
def third_parser(req_third):
	third_soup = BeautifulSoup(req_third.text, 'html')
	positions = third_soup.find_all('td', {'class': 'th'})
	for position in positions:
		post_url = position.find('a').attrs['href']
		post_request_info = requests.get('https://www.avariilised-autod.ee'+post_url+'&l=ru')
		post_soup = BeautifulSoup(post_request_info.text, 'html')
		post_req = html.fromstring(post_request_info.content)
		post_groups = post_soup.find_all('div', {'class': 'group'})
		equipment = '''
		Оснащение\n
		'''
		for group in post_groups[:7]:
			equipment += f'\n{group.find("h3").text.strip()}\n{group.find("h3").next_sibling}\n'
		car_name = post_req.xpath('//*[@id="vehicle_details"]/h1/text()')[0]
		
		car_text = f'{car_name}\n\n'
		car_trs = post_soup.find_all('tr', {'class': 'row'})
		for tr in car_trs:
			try:
				txt = f"{tr.find_all('td')[0].text.strip()}\n{tr.find_all('td')[1].text.strip()}\n\n"
				car_text += txt
			except:
				pass
		car_text += equipment
		params_text = '\n'
		technical_params = post_soup.find_all('div', {'class': 'box box2'})[1]
		for i in technical_params.find_all('td'):
			params_text += i.text.strip() + '\n'
		car_text += params_text
		car_name = f'avariilised - {car_name}'
		os.mkdir(car_name)
		with open(f'./{car_name}/'+car_name+'.txt', 'w') as f:
			f.write(car_text)
		pictures_a = post_soup.find_all('a', {'class': 'picture'})
		for a in range(len(pictures_a)):
			pic_url = pictures_a[a].find('img').attrs['src'].split('?')[0]
			image = requests.get('https://www.avariilised-autod.ee/vehicles/'+pic_url).content
			with open(f'./{car_name}/'+str(a)+'.jpg', 'wb') as f:
				f.write(image)
		shutil.make_archive(car_name, 'zip', car_name)
		shutil.rmtree(f'{car_name}/')
		with open('telegram.txt', 'r') as f:
			ids_list = f.read().split(',')
			for chat_id in ids_list:
				try:
					app.send_document(chat_id, open(car_name+'.zip','rb'))
				except:
					pass
		os.remove(car_name+'.zip')

def fourth_parser(soup):
	last_post_url = soup.find_all('div', {'class': 'oksjonid-list-item'})[-1].find('a', {'class': 'oksjonid-list-link'}).attrs['href']
	req_post = requests.get('https://romu.ee'+last_post_url)
	req_xpath = html.fromstring(req_post.content)
	post_soup = BeautifulSoup(req_post.text, 'html')
	page_soup = BeautifulSoup(req_post.content, 'html')
	trs = page_soup.find('div', {'class': 'component'}).find_all('div', {'class': 'row'})[1].find('div', {'class': 'col-xs-8'}).find('div', {'class': 'col-xs-7'}).find_all('tr')
	car_name = 'romu - ' + req_xpath.xpath('/html/body/div/div/div[2]/div/div[3]/div[1]/div/h1/text()')[0]
	text = f"{car_name}\nТекущая ставка - {req_xpath.xpath('/html/body/div/div/div[2]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div/h1/text()')[0]}\n"
	for tr in trs:
		text += f"\n{tr.find('th').text.strip()}\n{tr.find('td').text.strip()}\n"
	os.mkdir(car_name)
	with open(f'./{car_name}/'+car_name+'.txt', 'w') as f:
		f.write(text)
	images = post_soup.find_all('div', {'class': 'oksjonid-image'})
	for image in range(len(images)):
		img = requests.get(images[image].find('img').attrs['src'].replace('/thumbs', '')).content
		with open(f'./{car_name}/'+str(image)+'.jpg', 'wb') as f:
			f.write(img)
	shutil.make_archive(car_name, 'zip', car_name)
	shutil.rmtree(f'{car_name}/')
	with open('telegram.txt', 'r') as f:
		ids_list = f.read().split(',')
		for chat_id in ids_list:
			try:
				app.send_document(chat_id, open(car_name+'.zip','rb'))
			except:
				pass
	os.remove(car_name+'.zip')

def bot_thread():
	print('### START TELEGRAM ###')
	app.polling()

def parser_thread():
	print('### START PARSER ###')
	old_name = ''
	date_old = ''
	old_post_name = ''
	while True:
		# first
		try:
			print('checkout ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
			first_parser()
		except Exception as e: 
			print(e)

		# second
		req = requests.get('http://utbod.vis.is/default.aspx').text
		soup = BeautifulSoup(req, 'html')
		name = ''
		try:
			name = soup.find('span', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionTitle'}).text.strip()
		except Exception as e:
			print(e)
		try:
			if name != old_name:
				old_name = name
				print('checkout ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				second_parser(soup)
		except Exception:
			print(e)

		# third
		req_third = requests.get('https://www.avariilised-autod.ee/auctions/')
		tree = html.fromstring(req_third.content)
		date_web = tree.xpath('//*[@id="vehicle_search"]/div/div[1]/div/div/text()')[0].split(' ')[0]
		if date_old != date_web:
			date_old = date_web
			try:
				print('checkout ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				third_parser(req_third)
			except Exception as e:
				print(e)
		# fourth
		req_page = requests.get('https://romu.ee/ru/car-auctions?start=100000000000')
		page_soup = BeautifulSoup(req_page.text, 'html')
		post_name = page_soup.find('h2', {'class': 'okjsonid-list-details-title'}).text.strip()
		if old_post_name != post_name:
			old_post_name = post_name
			try:
				print('checkout ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				fourth_parser(page_soup)	
			except Exception as e:
				print(e)	
		time.sleep(30)

if __name__ == '__main__':
	thr_bot = threading.Thread(target=bot_thread)
	thr_bot.start()
	thr_parser = threading.Thread(target=parser_thread)
	thr_parser.start()
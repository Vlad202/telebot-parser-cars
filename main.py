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
	geted_id = message.chat.id
	with open('telegram.txt', 'r', encoding='utf-8') as f:
		ids_list = f.read().split(',')
		ids = ids_list
	if str(geted_id) not in ids:
		ids.append(str(geted_id))
		# print(message)
		with open('telegram.txt', 'a') as f:
			f.write(f'{str(geted_id)},')
	msg = '''
	Здравствуйте!\nТеперь вам будут присылаться новые объявления из сайтов:
	\nbilauppbod.is\nutbod.vis.is\navariilised-autod.ee\nromu.ee\notomoto.pl\n
	Чтоб отказатья от подписки, введите /stop
	'''
	app.send_message(geted_id, msg)

@app.message_handler(commands=['stop'])
def example_command(message):
	geted_id = message.chat.id
	with open('telegram.txt', 'r', encoding='utf-8') as f:
		ids_list = f.read().split(',')
	msg = '''
		ID пользователя не найдено, кажется что Вы ещё не подписаны на рассылку.Подписаться - /start
	'''
	if str(geted_id) in ids_list:
		ids_list.remove(str(geted_id))
		updated_ids_list = ','.join(str(x) for x in ids_list)
		with open('telegram.txt', 'w') as f:
			f.write(updated_ids_list)
		msg = '''
			Вам больше не будут рприходить сообщения от меня.\nЧто бы получать уведомления снова, введите команду /start
		'''
	app.send_message(geted_id, msg)

def send_zip(zip_name):
	with open('telegram.txt', 'r') as f:
		ids_list = f.read().split(',')
		for chat_id in ids_list:
			try:
				app.send_document(chat_id, open(zip_name+'.zip','rb'))
			except:
				pass	

def first_parser():
	URL = 'https://www.bilauppbod.is'
	global thumb_identify
	html = requests.get(URL).text
	soup = BeautifulSoup(html, 'html')
	post = soup.find_all("div", {"class": "auctionitem"})[-2]
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
		auction_info = post_details_soup.find('div', {'id': 'auction_info'})
		auction_pre_info = ''
		try:
			auction_pre_info += auction_info.find('h3').text.strip() + '\n'
		except:
			pass
		try:
			auction_pre_info += auction_info.find_all('p')[0].text.strip() + '\n'
		except:
			pass
		try:
			auction_pre_info += auction_info.find_all('p')[1].text.strip() + '\n'
		except:
			pass
		text = f'''
		{post_url}
		{auction_pre_info}
		Framleiðandi  - {table_rows[0].find_all('td')[-1].text.strip()}
		Skráð tjónaökutæki - {table_rows[1].find_all('td')[-1].text.strip()}
		Nýskráður  - {table_rows[2].find_all('td')[-1].text.strip()}
		Árgerð - {table_rows[3].find_all('td')[-1].text.strip()}
		Framleiðsluár - {table_rows[4].find_all('td')[-1].text.strip()}
		Fyrsti skráningard. - {table_rows[5].find_all('td')[-1].text.strip()}
		Fastanúmer - {table_rows[6].find_all('td')[-1].text.strip()}
		Litur - {table_rows[7].find_all('td')[-1].text.strip()}
		Gírar - {table_rows[8].find_all('td')[-1].text.strip()}
		Dyr - {table_rows[9].find_all('td')[-1].text.strip()}
		Akstur (km/mílur) - {table_rows[10].find_all('td')[-1].text.strip()}
		Vélargerð (eldsneyti) - {table_rows[11].find_all('td')[-1].text.strip()}
		Vélastærð (slagrými) - {table_rows[12].find_all('td')[-1].text.strip()}
		Seljandi - {table_rows[13].find_all('td')[-1].text.strip()}
		'''

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
		send_zip(files_name)	
		os.remove(files_name+'.zip')
		shutil.rmtree(f'{files_name}/')

def second_parser(soup, name):
	td_href = soup.find('a', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionLink'}).attrs['href']
	details_soup = BeautifulSoup(requests.get('http://utbod.vis.is/'+td_href).text, 'html')
	table = details_soup.find('table', {'id': 'carTable'})
	tr_list = table.find_all('tr')
	# time_now = str(datetime.datetime.today().strftime('%Y-%m-%d'))
	for tr in tr_list[1:]:
		tr_url = tr.find_all('td')[0].find('a').attrs['href']
		post_url = 'http://utbod.vis.is'+tr_url[2:]
		table_details = requests.get(post_url)
		tree = html.fromstring(table_details.content)
		try:
			astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/text()')[0]
		except IndexError:
			astand = tree.xpath('//*[@id="MainPage__ctl3_ItemDetails1_CarInfo1_Damaged"]/font/text()')[0]
		car_name = tree.xpath('//*[@id="MainPage__ctl3_nameofItem"]/text()')[0]
		car_text = f'''\n
		{post_url}\n
		{name}\n
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
			send_zip(car_name)
			os.remove(car_name+'.zip')
		
def third_parser(req_third, date_web):
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
		is_worked = post_req.xpath('//*[@id="vehicle_details"]/div[3]/div/ul/li[4]/text()')[0]
		car_text = f'{car_name}\n\n{is_worked}\n\nДата аукциона - {date_web}\n\n'
		car_trs = post_soup.find_all('tr', {'class': 'row'})
		for tr in car_trs:
			try:
				txt = f"{tr.find_all('td')[0].text.strip()}\n{tr.find_all('td')[1].text.strip()}\n\n"
				car_text += txt
			except:
				pass
		car_text += equipment
		params_text = f"\n{'https://www.avariilised-autod.ee'+post_url+'&l=ru'}\n"
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
		send_zip(car_name)
		os.remove(car_name+'.zip')

def fourth_parser(soup):
	last_post_url = soup.find_all('div', {'class': 'oksjonid-list-item'})[-1].find('a', {'class': 'oksjonid-list-link'}).attrs['href']
	post_url = 'https://romu.ee'+last_post_url
	req_post = requests.get(post_url)
	req_xpath = html.fromstring(req_post.content)
	post_soup = BeautifulSoup(req_post.text, 'html')
	page_soup = BeautifulSoup(req_post.content, 'html')
	trs = page_soup.find('div', {'class': 'component'}).find_all('div', {'class': 'row'})[1].find('div', {'class': 'col-xs-8'}).find('div', {'class': 'col-xs-7'}).find_all('tr')
	car_name = 'romu - ' + req_xpath.xpath('/html/body/div/div/div[2]/div/div[3]/div[1]/div/h1/text()')[0]
	text = f"{post_url}\n\n{car_name}\nТекущая ставка - {req_xpath.xpath('/html/body/div/div/div[2]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div/h1/text()')[0]}\n"
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
	send_zip(car_name)
	os.remove(car_name+'.zip')

def fivth_parser(post_url):
	response_post = requests.get(post_url)
	post_soup = BeautifulSoup(response_post.text, 'html')
	table_items = post_soup.find_all('li', {'class': 'offer-params__item'})
	car_name = post_soup.find('span', {'class': 'offer-title'}).text.strip()
	text = f"{post_url}\n\n{car_name}\n{post_soup.find('span', {'class': 'offer-price__number'}).text.strip()}\n\n\n"
	car_name = 'otomoto - '+car_name
	os.mkdir(car_name)
	for li in table_items:
		text += f"{li.find('span').text.strip()} - {li.find('div').text.strip()}\n\n"
	with open(f'./{car_name}/'+car_name+'.txt', 'w') as f:
		f.write(text)
	slick_slides = post_soup.find_all('li', {'class': 'offer-photos-thumbs__item'})
	for slide in range(len(slick_slides)):
		url = slick_slides[slide].find('img').attrs['src'].split(';s=')[0]
		image = requests.get(url).content
		with open(f'./{car_name}/'+str(slide)+'.jpg', 'wb') as f:
			f.write(image)
	shutil.make_archive(car_name, 'zip', car_name)
	shutil.rmtree(f'{car_name}/')
	send_zip(car_name)
	os.remove(car_name+'.zip')

def bot_thread():
	print('### START TELEGRAM ###')
	app.polling()

def parser_thread():
	print('### START PARSER ###')
	old_name = ''
	date_old = ''
	old_post_name = ''
	old_fivth = ''
	while True:
		# first
		try:
			print('checkout ------- billupload ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
			first_parser()
		except Exception as e: 
			print(e)

		# second
		req = requests.get('http://utbod.vis.is/default.aspx').text
		soup = BeautifulSoup(req, 'html')
		name = ''
		utbot_msg = 'checkout ------- utbod ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
		try:
			name = soup.find('span', {'id': 'pageTemplate__ctl3_rptrAuctions__ctl1_auctionTitle'}).text.strip()
		except AttributeError as e:
			print(utbot_msg)
		try:
			if name != old_name:
				old_name = name
				print(utbot_msg)
				second_parser(soup, name)
		except Exception:
			print(e)

		# third
		req_third = requests.get('https://www.avariilised-autod.ee/auctions/')
		tree = html.fromstring(req_third.content)
		date_web = tree.xpath('//*[@id="vehicle_search"]/div/div[1]/div/div/text()')[0].split(' ')[0]
		if date_old != date_web:
			date_old = date_web
			try:
				print('checkout ------- avariilised ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				third_parser(req_third, date_web)
			except Exception as e:
				print(e)
		# fourth
		req_page = requests.get('https://romu.ee/ru/car-auctions?start=100000000000')
		page_soup = BeautifulSoup(req_page.text, 'html')
		post_name = page_soup.find('h2', {'class': 'okjsonid-list-details-title'}).text.strip()
		if old_post_name != post_name:
			old_post_name = post_name
			try:
				print('checkout ------- romu ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				fourth_parser(page_soup)	
			except Exception as e:
				print(e)
		# fivth
		try:
			response_fivth = requests.get('https://www.otomoto.pl/osobowe/?search%5Bfilter_enum_damaged%5D=1&search%5Border%5D=created_at%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=')
		except Exception as e:
			print(e)
		fivth_soup = BeautifulSoup(response_fivth.text, 'html')
		first_car_fivth = fivth_soup.find_all('a', {'class': 'offer-title__link'})[0]
		first_car_fivth_text = first_car_fivth.text.strip()
		if first_car_fivth_text != old_fivth:
			try:
				print('checkout ------- otomoto ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				fivth_parser(first_car_fivth.attrs['href'])
			except Exception as e:
				print(e)
			old_fivth = first_car_fivth_text
		time.sleep(60)

if __name__ == '__main__':
	thr_bot = threading.Thread(target=bot_thread)
	thr_bot.start()
	thr_parser = threading.Thread(target=parser_thread)
	thr_parser.start()
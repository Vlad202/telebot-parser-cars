import requests
from bs4 import BeautifulSoup
import time
from telebot import TeleBot
import csv
import threading
import datetime
from secrets import TELEGRAM_TOKEN


chat_ids = []
URL = 'https://www.bilauppbod.is'
last_post = ''

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
	global last_post
	html = requests.get(URL).text
	soup = BeautifulSoup(html, 'html')
	post = soup.find_all("div", {"class": "auctionitem"})[-1]
	if not last_post:
		last_post = post
	if last_post != post:
		last_post = post
		print('new post')
		with open('telegram.txt', 'r') as f:
			ids_list = f.read().split(',')
			post_url = URL + last_post.find('h3').find('a').attrs['href']
			post_details = requests.get(post_url).text
			post_details_soup = BeautifulSoup(post_details, 'html')
			post_details_url = post_details_soup.find('div', {'id': 'auction_images'}).find_all('a')[0].attrs['href']
			# build text message
			table_rows = post_details_soup.find_all('tr')
			header = last_post.find('h3').find('a').text.strip()
			mileage = f"Пробег (км / мил):   {table_rows[10].find_all('td')[-1].text.strip()}"
			engine = f"Двигатель:   {table_rows[11].find_all('td')[-1].text.strip()}, объём {table_rows[12].find_all('td')[-1].text.strip()}"
			transmission = f"Коробка:   {table_rows[8].find_all('td')[-1].text.strip()}"
			registration = f"Дата первой регистрации:   {table_rows[5].find_all('td')[-1].text.strip()}"
			auction_date = f"Дата аукциона:   {post_details_soup.find('div', {'id': 'auction_bid'}).find('div', {'class': 'top'}).find_all('dd')[-1].text.strip()}"
			text = f"{header}\n\n{mileage}\n{engine}\n{transmission}\n{registration}\n{auction_date}"
			# get image
			image_url = URL + last_post.find('img').attrs['src']
			image = requests.get(URL + post_details_url).content
			for chat_id in ids_list:
				try:
					app.send_photo(chat_id, image, text)
				except:
					pass
	print('checkout ------- '+ last_post.find('h3').find('a').text.strip() +' -------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))


def bot_thread():
	print('### START TELEGRAM ###')
	app.polling()

def parser_thread():
	print('### START PARSER ###')
	while True:	
		try:
			main()
		except: 
			pass
		time.sleep(60)

if __name__ == '__main__':
	thr_bot = threading.Thread(target=bot_thread)
	thr_bot.start()
	thr_parser = threading.Thread(target=parser_thread)
	thr_parser.start()
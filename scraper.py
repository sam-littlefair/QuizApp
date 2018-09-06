import time
import requests
import sys

from colorama import init, Fore, Back, Style
init()

answer = ["","",""]
amount = [0,0,0]

query = sys.argv[1]
query = query.replace("passquotemark", '"')
answer[0] = sys.argv[2]
answer[1] = sys.argv[3]
answer[2] = sys.argv[4]

start_time = time.time()
isnot = 0
query = query.lower()
query += ' ((' + answer[0] + ') OR (' + answer[1] + ') OR (' + answer[2] + '))'
if 'did not ' in query or 'is not ' in query or 'was not ' in query or 'has not ' in query or 'does not ' in query or 'are not ' in query or 'is imaginary' in query:
	isnot = 1
	query = query.replace('not ', '')

query = query.replace(' ', '+')

count = [0,0,0]
for loop in range(0, 3):
	quote_page = 'https://www.googleapis.com/customsearch/v1?key=[YOUR_API_KEY]&cx=[YOUR_CX]&q=' + query + '&start=' + str(1+(loop * 10))
	page = requests.get(quote_page)

	result = page.text.lower()
	result = result[result.find('"items": ['):]

	if True:
		for x in range(0, 3):
			word = answer[x].lower()
			count[x] += result.count(word)
			
		if loop is 2:
			max = 0
			min = 1000000000000000
			ans = 0
			if isnot is 0:
				for x in range(0, 3):
					check = count[x]
					if max < check:
						max = check
						ans = x

			elif isnot is 1:
				for x in range(0, 3):
					check = count[x]
					if min > check:
						min = check
						ans = x	

			if count[0] is 0 and count[1] is 0 and count[2] is 0:
				print('I cannot make an accurate guess for this question..')
				
			else:
				total = count[0] + count[1] + count[2]
				print('==========================')
				print('CONFIDENCE RATING')
				print('==========================')
				print(answer[0] + ': ' + str(round((count[0] / total) * 100,2)) + '%')
				print(answer[1] + ': ' + str(round((count[1] / total) * 100,2)) + '%')
				print(answer[2] + ': ' + str(round((count[2] / total) * 100,2)) + '%')
				print('==========================')
				print('My guess is: ')
				if isnot is 0:
					if (count[ans]/total) < 0.8:
						print(Fore.YELLOW + answer[ans] + Fore.WHITE + ' (Not very confident)')
					elif(count[ans]/total) >= 0.95:
						print(Fore.GREEN + answer[ans] +Fore.WHITE + ' (VERY Confident)')
					else:
						print(Fore.GREEN + answer[ans] +Fore.WHITE + ' (Confident)')
				else:
					if (count[ans]/total) > 0.2:
						print(Fore.YELLOW + answer[ans]  +Fore.WHITE + ' (Not very confident)')
					elif(count[ans]/total) <= 0.05:
						print(Fore.GREEN + answer[ans] +Fore.WHITE + ' (VERY Confident)')
					else:
						print(Fore.GREEN + answer[ans] +Fore.WHITE + ' (Confident)')

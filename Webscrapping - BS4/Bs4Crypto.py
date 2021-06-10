from urllib.request import urlopen, Request
from win10toast import ToastNotifier
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
import re, os

C = 1
toaster = ToastNotifier()

class Crypto:
	def __init__(self):
		self.name = "Crypto"
		self.html = None

Price = []
Prices = {
	
}
urls = [
	"https://br.investing.com/crypto/bitcoin/btc-brl",
	"https://br.investing.com/crypto/ethereum/eth-brl",
	"https://br.investing.com/crypto/litecoin/ltc-brl",
	"https://br.investing.com/crypto/chiliz/chz-brl",
	"https://br.investing.com/crypto/monero/xmr-usd",
	"https://br.investing.com/crypto/binance-coin/bnb-brl",
	"https://br.investing.com/crypto/cardano/ada-brl",
	"https://br.investing.com/crypto/xrp/xrp-brl",
	"https://br.investing.com/crypto/wibx/wbx-brl",
	"https://br.investing.com/crypto/bitcoin-cash/bch-brl",
]

for url in urls:
	Prices.update({
		f"{url[-7:-4].upper()}-{url[-3:].upper()}":[]
	})

def CryptoScrap(CryptoUrls = urls):
	global C
	# Centralizar título
	Linhas = "==="*21
	Data = []
	print("==="*21)
	
	space = ""
	title = f"{space}https://br.investing.com/ {datetime.now().strftime('%D')}{space}"
	while len(title) < 61:
		space += " "
		title = f"{space}https://br.investing.com/ {datetime.now().strftime('%D')}{space}"
	print(title)
	print("==="*21)

	Data.append(Linhas)
	Data.append(title)
	Data.append(Linhas)
	with open("ResumeCrypto.txt","+a") as f:
		for d in Data:
			f.write(f"{d}\n")
	counter = 0
	temp = ""
	# Loop
	for url in CryptoUrls:
		CodeCoin = f"{url[-7:-4].upper()}-{url[-3:].upper()}"
		hdr = {"User-Agent": "Mozilla/5.0"} 							# Linha de comando utilizada para previnir o erro 503 (DENIED ACESS)
		req = Request(url,headers=hdr) 									# Entra na página como "User-Agent" usando o navegador Mozilla/5.0
		page = BeautifulSoup(urlopen(req),'html.parser') 				# Mostra o código url da página
		pattern = '<.*?id="last_last".*?>.*?<.*?>' 						# Padrão a ser buscado pelo módulo re
		
		# Coleta de hora do sistema
		now = datetime.now()

		# Coleta de resultado
		result = re.findall(pattern,str(page),re.IGNORECASE)			# re.IGNORECASE >>> Ignorar caixa alta
		
		# Processo de substituição de pontos e vírgulas
		
		for i in result:
			filtred = re.sub("<.*?>","",i)
			if "." in filtred and "," in filtred:
				filtred = filtred.replace(".","")
			if "," in filtred:
				filtred = float(filtred.replace(",","."))
		Prices[CodeCoin].append([filtred,now.strftime("%H:%M:%S")])

		spaces = ""
		msg = f' ({CodeCoin}) {filtred}{spaces}({now.strftime("%H:%M:%S")})'
		while len(msg) < 30:
			spaces += " "
			msg = f' ({CodeCoin}) {filtred}{spaces}({now.strftime("%H:%M:%S")})'
		
		if counter % 2 == 0 and (len(urls) - 1) > counter:
			print(msg,end=" |")
			temp = f"{msg} |"
			
		else:
			print(msg)
			Data.append(f"{temp}{msg}")
			temp = ""
			with open("ResumeCrypto.txt","+a") as f:
				f.write(f"{Data[-1]}\n")
		counter += 1
	C += 1
	sleep(1)
	return Prices
	
def main():
	Limite = 2.95
	while True:
		CryptoScrap()

if __name__ == '__main__':
	main()
	
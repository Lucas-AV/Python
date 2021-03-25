import requests, sqlite3, getpass, pathlib, wget, re, os
from urllib.request import urlopen, Request
from operator import itemgetter, attrgetter
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import pyautogui as ptg
import pandas as pd
import numpy as np

def BaseScrap(View=True):
	url = "https://www.worldometers.info/coronavirus/" # link para coleta de dados
	hdr = {"User-Agent": "Mozilla/5.0"} # Linha de comando utilizada para previnir o erro 503 (DENIED ACESS)
	req = Request(url,headers=hdr) # Entra na página como "User-Agent" usando o navegador Mozilla/5.0
	page = BeautifulSoup(urlopen(req),'html.parser') # Mostra o código url da página
	
	# Extra Info (All Countrys + Country Population)
	extra_info = page.select("div tbody tr td a") # Procura pelos paises dentro do código html 
	pattern = "<.*?>.*?<.*?>" # Padrão a ser procurado
	result = re.findall(pattern, str(extra_info), re.IGNORECASE) # Remove o padrão encontrado no código
	Filtr = [] # Lista para armazenar as informações básicas de cada país (Nome, População)
	for i in result:
		i = re.sub("<.*?>","",i) # Substitui todos os <>
		try:
			int(i.replace(",","")) # tenta transformar i em um inteiro
			Filtr[-1].append(i) # se o i for transformado em um inteiro com sucesso, a lista adiciona ele ao mesmo bloco do último país
		except:
			Filtr.append([i]) # Cria um bloco com o nome do pais atual do loop
	
	# Remove valores repetidos da lista original
	for i in Filtr[:]: # Nem todas as populações estão nessa lista, por exemplo a da china não aparece nessa lista mas aparece na outra coleta de dados
		if len(i) < 2: # Adiciona --- se o bloco não tiver um len > 2 (Nesse caso o --- vai ocupar o local da população no bloco)
			i.append('---') # preenche o vazio gerado pela falta da população
		if Filtr.count(i) >= 2:
			while Filtr.count(i) > 1:
				Filtr.remove(i) # Remove as repetições de i na lista original

	search = page.select("div tbody tr td") # Busca os dados dentro do código a partir do seu css selector
	
	Tot_Data = []
	# Dados específicos de cada país
	for Country in Filtr:
		country = Country[0] # começa o processo por meio do país contido no bloco Country (País -> index = 0, população -> index = 1)
		start = -1

		# Esse loop localiza a posição de Country no html
		for i in range(len(search)):
			if search[i].get_text().find(country) != -1:
				start = i
				break

		# Coleta de dados a partir da posição de Country
		data = [] # Local para armazenamento de dados
		for i in range(1,15): # Range de todos os dados fornecidos pelo site para cada país
			try:
				data += [search[start+i].get_text()] # Adição do valor confirmado
				if len(str(data[-1])) < 1 or data[-1] == " " or data[-1] == "N/A": # Se por acaso o valor de i for um vazio ele o substitui por 0 (Originalmente seria utilizado "Valor Não Informado")
					data[-1] = '0'
				chars = '0123456789,. /abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVXYWZ'
				nums = '0123456789'
				dotp = "."
				for n in data[-1]:
					if n not in chars:
						data[-1] = '0'
					if "," in data[-1]:
						try:
							data[-1] = data[-1].replace(",",'')
						except:
							pass
					if "." in data[-1]:
						data[-1] = int(float(data[-1])*100)
			except:
				data += [0]

		# Dict contendo todas as informações do código, pode ser útil para legendar os valores da lista gerada pelo código
		Info = {
			"Pais":country,
			"Total de casos":data[0],
			"Novos casos":data[1],
			"Total de mortes":data[2],
			"Novas mortes":data[3],
			"Total de recuperados":data[4],
			"Novos recuperados":data[5], # Não tenho certeza do que é esse data 5 porém de acordo com o padrão do código ele seria por lógica o valor de Novos Recuperados
			"Casos ativos":data[6],
			"Casos em estado crítico":data[7],
			"Casos por 1M de pessoas":data[8],
			"Mortes por 1M de pessoas":data[9],
			"Total de testes":data[10],
			"Testes por 1M de pessoas":data[11],
			"Populacao":data[12],
			"Continente":data[13],
		}

		# Print das informações
		if View:
			for In in Info:
				print(f'> {In}: {Info[In]}')
			print('')
		
		Tot_Data.append([Info[In] for In in Info]) # Adiciona as informações coletadas que estão no dict a uma lista para construção de um gráfico.
		
	# print(f"Coleta de dados feita do site: {url}\n") # Créditos ao site utilizado
	return Tot_Data

def CreateCSV_XLSX(RefList,Title="Covid",Range=None,DfOrd="Total_de_casos"):
	NamePlusCases = []
	for In in RefList:
		try: 
			int(In[14])
		except:
			NamePlusCases.append([
				In[0],int(In[1]),int(In[2]),
				int(In[3]),int(In[4]),int(In[5]),
				int(In[6]),int(In[7]),int(In[8]),
				int(In[9]),int(In[10]),int(In[11]),
				int(In[12]),int(In[13]),In[14],
			])
	NamePlusCases = sorted(NamePlusCases, key=itemgetter(1),reverse = True) # itemgetter(1) == total de casos
	DictFrame = {
		"Pais":[In[0] for In in NamePlusCases[0:Range]],
		"Total_de_casos":[In[1] for In in NamePlusCases[0:Range]],
		"Novos_casos":[In[2] for In in NamePlusCases[0:Range]],
		"Total_de_mortes":[In[3] for In in NamePlusCases[0:Range]],
		"Novas_mortes":[In[4] for In in NamePlusCases[0:Range]],
		"Total_de_recuperados":[In[5] for In in NamePlusCases[0:Range]],
		"Novos_recuperados":[In[6] for In in NamePlusCases[0:Range]], # Não tenho certeza do que é esse valor porém de acordo com o padrão do código ele seria por lógica o valor de Novos Recuperados (0 na maioria das vezes)
		"Casos_ativos":[In[7] for In in NamePlusCases[0:Range]],
		"Casos_em_estado_critico":[In[8] for In in NamePlusCases[0:Range]],
		"Casos_por_1M_de_pessoas":[In[9] for In in NamePlusCases[0:Range]],
		"Mortes_por_1M_de_pessoas":[In[10] for In in NamePlusCases[0:Range]],
		"Total_de_testes":[In[11] for In in NamePlusCases[0:Range]],
		"Testes_por_1M_de_pessoas":[In[12] for In in NamePlusCases[0:Range]],
		"Populacao":[In[13] for In in NamePlusCases[0:Range]],
		"Continente":[In[14] for In in NamePlusCases[0:Range]],
	}

	df = pd.DataFrame(DictFrame) # Cria um DataFrame para ser convertido em .csv ou xlsx (Excel)
	df = df.sort_values([DfOrd], ascending=False).reset_index(drop=True) # Organiza o DataFrame de acordo com o valor fornecido dentro de sort_values

	# Conversão
	df.to_csv(f'{Title}.csv')
	df.to_excel(f'{Title}.xlsx')

	# Retorna o DataFrame para ser utilizado em outras funções
	return DictFrame
	
def EasyDB(File):
	# Link para o site que estou utilizando para realizar uma conversão simples para banco de dados
	url = "https://beautifytools.com/excel-to-sql-converter.php"

	# Configurações do webdriver para o Selenium
	options = webdriver.ChromeOptions()
	options.add_argument('lang=pt-br')
	options.add_argument("disable-infobars")
	options.add_experimental_option("detach", True)

	# Pega o path atual do script e utiliza para rodar o chrome driver
	# ATENÇÃO: DEIXE O CHROMEDRIVER.EXE NA MESMA PASTA QUE O SEU SCRIPT.PY
	ActualPath = os.getcwd()
	driver_path = ActualPath + "\\chromedriver.exe"
	driver = webdriver.Chrome(driver_path, options=options)
	driver.get(url)

	# Pega o path do modelo salvo em Excel. (Posteriormente será utilizado para criação de um arquivo data.txt contendo comandos para criação de banco de dados)
	xlsx_path = str(pathlib.Path(File).parent.absolute())
	

	# Identifica alguns objetos necessários para conversão
	BROWSE_BTN = driver.find_element_by_id('browse') # Serve para procurar um arquivo no caso vamos usar o xlsx_path
	INSERT_BTN = driver.find_element_by_id('sql_insert') # Serve para criar o DB
	UPDATE_BTN = driver.find_element_by_id('sql_update') # Serve para atualizar o DB
	DELETE_BTN = driver.find_element_by_id('sql_delete') # Por padrão não será utilizado
	DOWNLOAD_BTN = driver.find_element_by_id('download') # Baixa os comandos disponibilizados


	# Processo para dar o upload do arquivo Excel gerado.
	BROWSE_BTN.click() # Clica no botão de browse (Buscar por arquivo)
	sleep(5)
	ptg.write(f"{xlsx_path}\\{File}") # Digita o path do arquivo Excel + o seu nome
	sleep(1)
	ptg.press('enter') # Envia o arquivo


	# Processo para decidir se o arquivo gerado vai ser para dar update ou insert
	if 'CovidIn.db' in os.listdir():
		UPDATE_BTN.click()
	else:
		INSERT_BTN.click()

	sleep(3)
	DOWNLOAD_BTN.click() # Faz o download do comando gerado
	sleep(3)
	driver.close()

	# Move o arquivo baixado
	username = str(getpass.getuser()) # Pega o seu username
	Download_Path = f'C:\\Users\\{username}\\Downloads'
	Pattern_Name = 'data.txt'
	sleep(5)
	os.replace(f'{Download_Path}\\{Pattern_Name}',f"{xlsx_path}\\{Pattern_Name}") # Coloca o arquivo baixado (data.txt) na mesma pasta que o Excel (Covid.xlsx)

def ExecuteScript():
	CovidData = BaseScrap(False)
	CreateCSV_XLSX(RefList=CovidData)
	TargetFile = 'Covid.xlsx'
	EasyDB(File=TargetFile)
	

import os
import sys
import json
import requests
from threading import Thread
from urllib.parse import urlparse

class bcolors:
   GREEN = '\033[92m'
   BGREEN = '\033[1;92m'
   RED = '\033[91m'
   BRED = '\033[1;91m'
   YELLOW = '\033[93m'
   BYELLOW = '\033[1;93m'
   BLUE = '\033[94m'
   BBLUE = '\033[1;94m'
   WHITE = '\033[97m'
   BWHITE = '\033[1;97m'
   ENDC = '\033[0m'

host = sys.argv[1]

APIKEY="01ab2b1fb310f916bb05763ed1d6e206d87ddf83d08c0147474a24b0c38ba160"
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'}

def save(item):
	with open(f"subdomain.list", 'a') as outlist:
		outlist.write('%s\n' % item)
	outlist.close()

#FUNTIONS FOR SUBDOMAIN ENUMARATION			
def crt(host):
	count = 0
	url = "https://crt.sh/?q=%25." + host + "&output=json" #%25 gives more results.
	while True:
		try:
			r = requests.get(url, headers=header)
		except:
			#RETRY
			continue
		break
	try:
		values = r.json()
		for i in values:
			domains = i['name_value']
			save(domains)
			count = count + 1
	except:
		pass
	print(f"{bcolors.BGREEN}[*]{bcolors.ENDC} Crt.sh: "+str(count))
				
def alienvault(host):
	count = 0
	url = "https://otx.alienvault.com/api/v1/indicators/domain/" + host + "/passive_dns"
	while True:
		try:
			r = requests.get(url, headers=header)
		except:
			#RETRY
			continue
		break
	try:
		values = r.json()
		domains = values['passive_dns']
		for i in domains:
			subdomain = i['hostname']
			save(subdomain)
			count = count + 1
	except:
		pass
	print(f"{bcolors.BGREEN}[*]{bcolors.ENDC} Alien Vault: "+str(count))
		
def virustotal(host):#USING API HERE
	count = 0
	url = "https://www.virustotal.com/vtapi/v2/domain/report?domain=" + host + "&apikey=" + APIKEY
	while True:
		try:
			r = requests.get(url, headers=header)
		except:
			#RETRY
			continue
		break
	try:
		values = r.json()
		domains = values['subdomains']
		for i in domains:
			save(i)
			count = count + 1
	except:
		pass
	print(f"{bcolors.BGREEN}[*]{bcolors.ENDC} Virus Total: "+str(count))
	
def anubis(host):	
	count = 0
	url = "https://jonlu.ca/anubis/subdomains/" + host
	while True:
		try:
			r = requests.get(url, headers=header)
		except:
			#RETRY
			continue
		break
	try:
		subdomains = r.json()
		for subdomain in subdomains:
			save(subdomain)
			count = count + 1
	except:
		pass
	print(f"{bcolors.BGREEN}[*]{bcolors.ENDC} Anubis DB: "+str(count))
	
def webarchive(host):
	count = 0
	url = "https://web.archive.org/cdx/search/cdx?url=" + host + "/&output=json&fl=original&collapse=urlkey&matchType=domain"
	#RETRY REQUESTS WHEN CONNECTION FAILS 
	while True:
		try:
			response = requests.get(url, headers=header)
		except:
			#RETRY
			continue
		break
	try:
		data = response.json()
		del data[0]#Removes first array
		for i,item in enumerate(data):
			data[i] = urlparse(item[0]).netloc
		data = sorted(set(data))
		for subdomain in data:
			if ":" in subdomain:
				subdomain = subdomain.split(":")[0]
			save(subdomain)
			count = count + 1
	except:
		pass
	print(f"{bcolors.BGREEN}[*]{bcolors.ENDC} Web Archive: "+str(count))

process = [crt, alienvault, virustotal , anubis, webarchive]
threads = []


for run in process:
	threads.append(Thread(target=run, args=(host,)) )

for thread in threads:
	thread.start()
	
for thread in threads:
	thread.join()

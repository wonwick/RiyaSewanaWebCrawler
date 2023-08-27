import requests
import lxml
from bs4 import BeautifulSoup
import csv
import string

def remove_non_ascii(a_str):
    ascii_chars = set(string.printable)

    return ''.join(
        filter(lambda x: x in ascii_chars, a_str)
    )



filename = "vehicles.csv"
rows=[]
with open(filename) as f:
    reader = csv.reader(f)
    rows = [row for row in reader]
#print (rows)
    
rows = [i for i in rows if i != []]
existingUrls=[]
for x in rows:
    ##print(x)
    existingUrls.append(x[1])


url = "https://riyasewana.com/search/toyota/aqua/2014-0"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
response = session.get(url)
soup = BeautifulSoup(response.content,'lxml')
##print (soup)
print("---------------------------------------------------")

paginations=soup.find('div',{'class':'pagination'}).find_all('a')
numberOFPages=len(paginations)
pageUrls=[]
                 
if(numberOFPages>0):
    for i in range(numberOFPages):
        if(i>0 and i<(numberOFPages-1)):
            pageUrl=paginations[i].get('href')
            pageUrls.append("https:"+pageUrl)
           #print (paginations[i].get('href'))

newRows=[]             

def crawl(NewUrl):
    
    soup=BeautifulSoup(session.get(NewUrl).content,'lxml')
    vehicleList=soup.find_all('li',{'class':'item round'})
    ##print(vehicleList[0])

    for i in vehicleList:
        
        vehicleData=i.find('a')
        vehicleTitle=vehicleData.get('title')
        vehicleUrl=vehicleData.get('href')
        if(vehicleUrl in existingUrls):
            continue

        
        vehicleinfo=i.find('div',{'class':'boxtext'}).find_all('div');
        called=False;
        sold=False

        #print("\n"+str(len(vehicleinfo)))
        #print(vehicleinfo)
        location=vehicleinfo[0].string
        price=vehicleinfo[1].string
        
        if(len(vehicleinfo)>3):
            milege=vehicleinfo[2].string
            date=vehicleinfo[3].string
        
        else:
            milege= "not available"
            date=vehicleinfo[2].string
        
        
        
        vehiclePage = session.get(vehicleUrl)
        vehicle=BeautifulSoup(vehiclePage.content,'lxml').find('table',{'class':'moret'}).find_all('tr');
        
        contact=vehicle[2].find('span').string
        YOM=vehicle[5].find_all('td')[1].string
        options=vehicle[7].find_all('td')[1].string
        details=vehicle[8].find_all('td')[1].get_text()
        newRows.append([vehicleTitle,vehicleUrl,date,location,price,contact,milege,YOM,options,remove_non_ascii(details),called,sold])

print ("started crawling")

crawl(url)
for i in pageUrls:
    crawl(i)

print("found "+str(len(rows))+' existing vehicles and added '+str(len(newRows))+ " new vehicles")

print("ended crawling")

rows.extend(newRows)
      
with open(filename, 'w') as csvfile:

    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(rows)

print ("ended writing")



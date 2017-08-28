import requests
import json
import time



def find_first_country(): #finding first country element in the JSON file (to skip regional level data)
    for element in jsondata:
        if not element['country']['value']=="Afghanistan":
            continue
        else:
            flag=jsondata.index(element)
            break
    return flag

def write_data(country, countryname, ind): #getting a necessary indicator for a country-year, modify years if needed
    try:
        url='http://api.worldbank.org/countries/'+country+'/indicators/'+ind+'?date=2002:2010&format=json'
        data=requests.get(url, timeout=10).text
        jsondata=json.loads(data)
        datastr=''
        for i in range(len(jsondata[1])-1, -1, -1):
            try:
                datastr=datastr+countryname+','+jsondata[1][i]['date']+','+jsondata[1][i]['value']+'\n'
            except TypeError: # in case the date is present and the value is absent
                datastr=datastr+countryname+','+jsondata[1][i]['date']+',\n'
        return datastr
    
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        time.sleep(10)
        return write_data(country, countryname, ind)
    except requests.packages.urllib3.exceptions.MaxRetryError:
        time.sleep(300)
        return write_data(country, countryname, ind)
    except Exception: #in case of missing or invalid response
        datastr=countryname+",\n"
        return datastr

#getting data on the population for all countries:
url='http://api.worldbank.org/countries/all/indicators/SP.POP.TOTL?date=2009&per_page=400&format=json'
data=requests.get(url).text

jsondata=json.loads(data)[1]

flag=find_first_country()
jsondata=jsondata[flag:len(jsondata)] #removing regional-level data(from the beginning of the JSON document)
    
        
##adding countries with more than 1 million people in 2009 to the new dataset (modify if not needed):

jsondataclean=[]

for element in jsondata:
    if float(element['value'])>1000000:
       jsondataclean.append(element)


countrylist=[]
for element in jsondataclean:
    element['country']['value']=element['country']['value'].replace(",", "")
    countrylist.append([element['country']['id'], element['country']['value']]) #list with country IDs and names; not a dictionary because I need to keep an order
#add and remove necessary indicators 
indicators=['NY.GDP.PCAP.KD', 'NY.GDP.PCAP.PP.KD', 'NY.GDP.PETR.RT.ZS', 'NY.GDP.NGAS.RT.ZS','SP.DYN.IMRT.IN', 'NY.GDP.MINR.RT.ZS', 'RL.EST', 'SP.DYN.LE00.IN']

datastr=''

for ind in indicators:
    with open('data '+ind+'.csv',"w") as f:
        f.write('country,year,'+ind+'\n')
        for country in countrylist:
            dt=write_data(country[0], country[1], ind)
            f.write(dt)
            print(country[1],' done')
    print(ind, ' done')

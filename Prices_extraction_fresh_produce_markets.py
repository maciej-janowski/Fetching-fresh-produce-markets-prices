from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import easygui


source = requests.get('https://www.zjazdowa.com.pl/pl/serwis-cenowy/').text

check_counter = 0
soup = BeautifulSoup(source,'lxml')

tables = soup.find_all('table')

check_df = pd.read_excel('csv_database\ceny_zjazdowa.csv',parse_dates=[5])

# loop through all tables and then pull each product and there min and max price

df = pd.DataFrame(columns=['product','origin','quantity','lowest_price','highest_price'])

# checking what is the current date
starting = soup.find('p',class_='text-right').text.split('\n')[1].find(": ") +2
when = soup.find('p',class_='text-right').text.split('\n')[1][starting:]
when_converted = datetime.datetime.strptime(when,'%d-%m-%Y')
    
# when_checked = datetime.date(when_converted)

if when_converted.date() not in check_df.date.dt.date.unique():
    # looping over all found tables
    for loop_no,tb in enumerate(tables[:-1],start=1):
        # finding all rows with data
        tds = tb.find_all('td')
        # assigning counter to 
        counter=0
        # creating dataframe
        df = pd.DataFrame(columns=['product','origin','quantity','lowest_price','highest_price','date'])
        # looping over all rows
        for x in tds:
            # creating empty dictionary to add to the dataframe
            row_to_add = {}
            # pulling each row for data extraction
            check = tds[0+counter:4+counter]
            # assigning proper values to dictionary
            row_to_add['product'] = check[0].text
            if loop_no==1:
                row_to_add['origin'] = 'import'
            elif loop_no==2:
                row_to_add['origin'] = 'krajowe'
            elif loop_no==3:
                row_to_add['origin'] = 'import'
            elif loop_no==4:
                row_to_add['origin'] = 'krajowe'
            row_to_add['quantity'] = check[1].text
    
            row_to_add['lowest_price'] = float(check[2].text.replace(",","."))
       
            row_to_add['highest_price'] = float(check[3].text.replace(",","."))
            row_to_add['date'] = when_converted
            counter+=4
            # adding arranged row to dataframe
            df = df.append(row_to_add,ignore_index=True)

            # if we went through all rows - we break the loop
            if counter==len(tds):
                break
            # converting data to floats
            
            # df['lowest_price'] = df['lowest_price']
            # df['highest_price'] = df['highest_price']
            # appending new data to our database

        check_df = check_df.append(df,ignore_index=True)
        

    check_df.to_csv('csv_database\ceny_zjazdowa.csv',index=False)
    check_counter+=1
else:
    print("Data for current day is already saved")
    easygui.msgbox("Information for current date is already saved for ZJAZDOWA Market", title="Data processed")


# GIEŁDA BRONISZE

# procedure for checking if data is already downloaded
when_checked = datetime.datetime.today().date()

check_df = pd.read_excel('csv_database\ceny_bronisze.xlsx')

data_dates = check_df['date'].dt.date.unique()
if when_checked not in data_dates:

    # gett data from the website
    source = requests.get('https://wiescirolnicze.pl/ceny-rolnicze/firmy/bronisze-warszawski-rolno-spozywczy-rynek-hurtowy-sa/').text

    soup = BeautifulSoup(source,'lxml')

    # finding relevant table
    table = soup.find('div',class_='table-responsive')

    # opening file with data in excel
    check_df = pd.read_csv('csv_database\ceny_.csv',parse_dates=[4])

    # finding all rows in the table
    tds = table.find_all('td')

    # creating dataframe for adding the data
    df_bronisze = pd.DataFrame(columns=['product','lowest_price','highest_price','date'])
    counter=0
    # looping over all rows and adding relevant data
    for x in tds:
        row_to_add = {}
        check = tds[0+counter:4+counter]
        row_to_add['product'] = check[0].text
        if len(check[1].text)<2:
            pricing = 0
        else:
            pricing = float(check[1].text.replace(',','.'))
        row_to_add['lowest_price'] = pricing
        row_to_add['highest_price'] = float(check[2].text.replace(',','.'))
        row_to_add['date'] = datetime.datetime.strptime(check[3].text,'%d.%m.%Y')
        counter+=4
        if counter==len(tds):
            break
        df_bronisze = df_bronisze.append(row_to_add,ignore_index=True)
    # getting data only for current day
    df_bronisze_check = df_bronisze[df_bronisze['date'].dt.date==when_checked]
    length = df_bronisze_check.shape[0]

    if length != 0: 
        # generating message that data for current day already exists
        print("Data for current day is already saved")
        easygui.msgbox("Information for current date is already saved for BRONISZE Market", title="Data processed")
    else:
        # splitting product column so that we have name and quantity

        splitting = df_bronisze['product'].str.split(',',expand=True)

        # function for checking the quantity
        def checking_value(source_name,origin_value):
            if origin_value !=None:
                return origin_value
            elif 'kraj' in source_name:
                return 'kraj'
            elif 'import' in source_name:
                return 'import'
            else:
                return "Nieznane"
        
        # concatenating frames
        new_df_bronisze = pd.concat([df_bronisze,splitting],axis=1)
        # removing irrelevant column
        new_df_bronisze.drop(columns=['product'],axis=1,inplace=True)

        # renaming columns
        new_df_bronisze.rename(columns={0:'product',1:'origin'},inplace=True)

        # adjusting text in product column
        new_df_bronisze['product'] = new_df_bronisze['product'].apply(lambda x:x[1:])

        # adjusting text in origin column
        # new_df_bronisze['origin'] = new_df_bronisze['origin'].apply(lambda x:x[3:-1])
        new_df_bronisze['origin'] = new_df_bronisze.apply(lambda x: checking_value(x['product'][-6:],x['origin']),axis=1)
        # rearranging column
        new_df_bronisze = new_df_bronisze[['product','origin','lowest_price','highest_price','date']]
        new_df_bronisze = new_df_bronisze[new_df_bronisze['date']==new_df_bronisze['date'].value_counts().index[0]]
        # adding new data and savingi the file to excel
        check_df = check_df.append(new_df_bronisze,ignore_index=True)
            
        check_df.to_csv('csv_database\ceny_bronisze.csv',index=False)
        check_counter+=1
else:
    # generating message that data for current day already exists
    print("Data for current day is already saved")
    easygui.msgbox("Information for current date is already saved for BRONISZE Market", title="Data processed")


# HANDLING ELIZOWKA

source = requests.get('https://www.elizowka.pl/notowania-cen-produktow').text

soup = BeautifulSoup(source,'lxml')

tables = soup.find('div',id='notowania')

kiedy = tables.find('small').text.split(':')[1].strip()

wartosc = tables.find_all('table')

warzywa = wartosc[1]
owoce = wartosc[2]

df = pd.read_csv(r'excel_database\ceny_elizowka.csv')

if kiedy not in df['date'].unique():
    warzywniak = warzywa.find_all('td')
    sad = owoce.find_all('td')

    # creating dataframe for adding the data
    df_elizowka = pd.DataFrame(columns=['product','measure','lowest_price','highest_price','date'])
    # empty list and counter for adding new values
    dicts_list = []
    counter=0
    # loop till iterator is exhausted
    for x in warzywniak:
        row_to_add = {}
        print(warzywniak[1+counter])
        row_to_add['product'] = warzywniak[1+counter].text
        row_to_add['measure'] = warzywniak[2+counter].text
        row_to_add['lowest_price'] = float(warzywniak[3+counter].text.split(' ')[0])
        row_to_add['highest_price'] = float(warzywniak[4+counter].text.split(' ')[0])
        row_to_add['date'] = kiedy
        dicts_list.append(row_to_add)
        counter +=8
        print('counter',counter)
        print('len',len(warzywniak))
        # exit loop when no more vegetables
        if counter >= len(warzywniak):
            break
    # appending resluts
    df_elizowka = df_elizowka.append(dicts_list,ignore_index=True)
    print(df_elizowka)
    # empty list and counter for adding new values
    dicts_list=[]
    counter = 0
    # loop till iterator is exhausted
    for x in sad:
        row_to_add = {}
        row_to_add['product'] = sad[1+counter].text
        row_to_add['measure'] = sad[2+counter].text
        row_to_add['lowest_price'] = float(sad[3+counter].text.split(' ')[0])
        row_to_add['highest_price'] = float(sad[4+counter].text.split(' ')[0])
        row_to_add['date'] = kiedy
        dicts_list.append(row_to_add)
        counter +=8
            # exit loop when no more vegetables
        if counter >= len(sad):
            break
    # appending results
    df_elizowka = df_elizowka.append(dicts_list,ignore_index=True)
    # creating new dataframe with old and new results
    df = df.append(df_elizowka,ignore_index=True)
    # dumping to excel
    df.to_csv('csv_database\ceny_elizowka.csv',index=False)
    print('Elizówka data is saved')
    check_counter +=1
else:
    easygui.msgbox("Information for current date is already saved for ELIZÓWKA Market", title="Data processed")


if check_counter==3:
     easygui.msgbox("Program has stopped retrieving the data", title="Data processed")

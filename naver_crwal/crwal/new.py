
from urllib.request import urlopen
import bs4
import requests
import sqlite3

conn = sqlite3.connect("disease2.db")
cur = conn.cursor()

cur.execute("delete from disease")
cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'disease'")
#######################################################
#           테이블명 : disease                         #
#           name : 병의이름                            #
#           define : 병의 정의                         #
#           reason : 병의 원인                         #
#           symptom : 증상                            #
#           diagnosis : 진단                          #
#           cure : 치료                               #
#           inspection : 검사                         #
#           prevention : 예방                         #
#           addi : 합병증                              #
#           guide : 가이드                             #
#           therapy : 식이요법                          #
#           sub : 하위질병                              #
########################################################


page_num = 1
address = 'https://www.naver.com'

crawling_data = requests.get(address)  # address에 access해서, data crawling하기

with conn:
    key = 1
    while True:

        main_url = "https://terms.naver.com/list.nhn?cid=51007&categoryId=51007" + "&page=" + str(page_num)
        main_html = urlopen(main_url)

        bs_obj = bs4.BeautifulSoup(main_html, "html.parser")
        content_list = bs_obj.find("ul", {"class": "content_list"})

        subjects = content_list.findAll("div", {"class": "subject"})

        # print(subjects)

        print('페이지 번호 : ' + str(page_num))

        for subject in subjects:

            index = 0
            a_tag = subject.find("a")
            sub_url = "https://terms.naver.com" + a_tag.get('href')
            sub_html = urlopen(sub_url)  # 각 질병 페이지의 URL

            bs_obj2 = bs4.BeautifulSoup(sub_html, "html.parser")  # 질병 페이지의 bs오브젝트 만들기

            disease_name = bs_obj2.find("title").text  # 질병의 이름
            h3_tags = bs_obj2.findAll("h3", {"class": "stress"})  # 증상, 원인, 하위질병 등 목차
            p_tags = bs_obj2.findAll("p", {"class": "txt"})  # 질병에 대한 정보(정의, 증상 등)

            cur.execute("insert into disease(name) values(?) ", (disease_name,))

            print('병명 : ' + disease_name + '\n')

            while(len(h3_tags) > len(p_tags)):
                p_tags.append(crawling_data)

            while(len(h3_tags) < len(p_tags)):
                h3_tags.append(crawling_data)

            for h3 in h3_tags:  # 각 질병의 정보 가져오기(림프종 및 고지혈증 목차 기준)

                if (h3.text == '정의'):
                    cur.execute("UPDATE disease SET define = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '원인'):
                    cur.execute("UPDATE disease SET reason = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '증상'):
                    cur.execute("UPDATE disease SET symptom = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '진단'):
                    cur.execute("UPDATE disease SET diagnosis = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '검사'):
                    cur.execute("UPDATE disease SET inspection = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '치료'):
                    cur.execute("UPDATE disease SET cure = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '경과/합병증'):
                    cur.execute("UPDATE disease SET addi = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '예방방법'):
                    cur.execute("UPDATE disease SET prevention = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '생활 가이드'):
                    cur.execute("UPDATE disease SET guide = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '식이요법'):
                    cur.execute("UPDATE disease SET therapy = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                elif (h3.text == '하위질병'):
                    cur.execute("UPDATE disease SET sub = (?) where id = (?)", (p_tags[index].text, key,))
                    index += 1

                else:
                    index += 1

            key+=1


        page_num +=1

        if(page_num ==91):break
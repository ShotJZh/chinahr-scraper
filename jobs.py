#! usr/bin/env python 3
# __*__ coding:utf-8 __*__


import requests
from lxml import etree
from selenium import webdriver
import json
from bs4 import BeautifulSoup
import re


def getdetailinfo(joburl, positionname,cityname):
    isvalid = True
    urlop = requests.get(joburl, headers=headers)
    html = urlop.text
    soup = BeautifulSoup(html, 'lxml')

    try:
        jobname = soup.select("span[class='job_name']")
    except:
        return "", "", "", "", "", False
    if len(jobname) == 0:
        return "", "", "", "", "", False
    jobname = jobname[0].text

    try:
        jobinfo = soup.select("div[class='job_intro_info']")
    except:
        return "", "", "", "", "", False
    if len(jobinfo) == 0:
        return "", "", "", "", "", False
    jobinfo = jobinfo[0].text

    if len(positionname)>2:
        testname = positionname[:3]
    else:
        testname = positionname
    if testname not in jobname and testname not in jobinfo:
        return "", "", "", "", "", False

    try:
        salary = soup.select("span[class='job_price']")
    except:
        return "", "", "", "", "", False
    if len(salary) == 0:
        return "", "", "", "", "", False
    salary = salary[0].text
    for i in salary:
        if re.match(r'^[\u4e00-\u9fa5],{0,}$',i):
            return "", "", "", "", "", False
    salary = salary.split('-')
    salary = str((int(salary[0]) + int(salary[1])) / 2)
    if(float(salary) < 1000):
        return "", "", "", "", "", False

    try:
        education = soup.select("div[class='job_require']")
    except:
        return "", "", "", "", "", False
    if len(education) == 0:
        return "", "", "", "", "", False
    education = education[0].contents
    if(len(education)<14):
        return "", "", "", "", "", False
    education = education[13].text

    try:
        experience = soup.select("span[class='job_exp']")
    except:
        return "", "", "", "", "", False
    if len(experience) == 0:
        return "", "", "", "", "", False
    experience = experience[0].text

    print(cityname,positionname,jobname,salary,education,experience)
    return joburl, jobname, salary, education, experience, isvalid


def getpositioninfo(cityname, positionname, positionurl):
    urlop = requests.get(positionurl, headers=headers)
    html = urlop.text
    page = etree.HTML(html)
    jobs = page.xpath("//div[@class='jobList']/ul/li[@class='l1']/span[@class='e1']/a")
    for job in jobs:
        joburl, jobname, salary, education, experience, isvalid = getdetailinfo(job.get('href'), positionname, cityname)
        if isvalid:
            data = {'city': cityname, 'position': positionname, 'salary': salary, 'education': education,
                    'experience': experience, 'jobname':jobname, 'joburl': joburl}
            json.dump(data, f)
    nextpage = page.xpath('''//a[@onclick="clickLog('from=chr_list_fastpage_next');"]''')
    while len(nextpage):
        nexturl = nextpage[0].get('href')
        urlop = requests.get(nexturl, headers=headers)
        html = urlop.text
        page = etree.HTML(html)
        jobs = page.xpath("//div[@class='jobList']/ul/li[@class='l1']/span[@class='e1']/a")
        for job in jobs:
            joburl, jobname, salary, education, experience, isvalid = getdetailinfo(job.get('href'), positionname,cityname)
            if isvalid:
                data = {'city': cityname, 'position': positionname, 'salary': salary, 'education': education,
                        'experience': experience, 'jobname': jobname, 'joburl': joburl}
                json.dump(data, f)
        nextpage = page.xpath('''//a[@onclick="clickLog('from=chr_list_fastpage_next');"]''')


def getcityinfo(city):
    url = 'http://www.chinahr.com/'+city+'/jobs/'
    browser = webdriver.PhantomJS(executable_path=r'C:\Users\skyri\Downloads\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    browser.get(url)
    browser.find_element_by_xpath("/html/body/div[2]/div[4]/div/div[1]/div[2]").click()
    html = browser.page_source
    page = etree.HTML(html)
    cityname = page.xpath("//*[@id='yc_tnav']/div/div[1]/span/em")
    cityname = cityname[0].text
    positions = page.xpath("//div[@class='item-con cur']/div/div/a")
    #选出待分析的行业
    positions = positions[0:13]+positions[26:28]+positions[29:32]+positions[36:38]+positions[42:43]+positions[44:45]+positions[48:49]+positions[54:56]+positions[68:69]+positions[74:76]
    for position in positions:
        getpositioninfo(cityname, position.text, position.get('href'))
    browser.quit()

headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/"
                          "22.0.1207.1 Safari/537.1"}
f = open('jobsData.json', 'w')
citys = ['shanghai']
for city in citys:
    getcityinfo(city)
f.close()


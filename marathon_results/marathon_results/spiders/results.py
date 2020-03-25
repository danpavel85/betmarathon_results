# -*- coding: utf-8 -*-
import scrapy
import mysql.connector
import datetime
from scrapy_splash import SplashRequest







class MarathonSpider(scrapy.Spider):
    name = 'results'


    script = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  assert(splash:runjs('document.querySelector("table.week-date-selector-component > tbody > tr > td:nth-of-type(2)").click()'))
  assert(splash:wait(7.5))
  return {
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
  }
end

    '''


    def start_requests(self):
        url = 'https://www.betmarathon.com/en/results.htm'
        yield SplashRequest(url=url, callback=self.parse, endpoint='execute', args={'wait': 5.5, 'lua_source': self.script})


    def parse(self, response):
        day_mounth = response.xpath("//td[@class='week-date-selector-item selected']/text()[1]").extract_first()
        day_mounth_replace1 = day_mounth.replace(' ', '#', 1)
        day_mounth_replace2 = day_mounth_replace1.replace(' ', '')
        day1, mounth1 = day_mounth_replace2.split('#')
        now = datetime.datetime.now()
        now_year = now.year
        now_year1 = str(now_year)
        day2 = str(day1)
        mounth2 = str(mounth1)
        current_date = now_year1 + '-' + mounth2 + '-' + day2
        datetime_object = datetime.datetime.strptime(current_date, '%Y-%B-%d').date()

        


        for div in response.xpath("//div[@class='result-sport-label'][contains(text(),'Football')]/parent::div/parent::div/parent::div[@class='result-sport']//div[@class='result-category']"):
            leagues = div.xpath(".//div[@class='category-label']/text()").extract_first()
            league_list = []
            league_replace = leagues.replace('. ', '#', 1)
            league_list.append(league_replace)
            country, league = zip(*(s.split("#") for s in league_list))
            cl = str(country) + "_" + str(league)
            cl_rep = cl.replace("('", '')
            cl_rep = cl_rep.replace("',)", '')
            cl_rep = cl_rep.replace('("', '')
            cl_rep = cl_rep.replace('",)', '')

            match = div.xpath(".//div[@class='result-event-label']")
            for x in match:
                try:
                    match_list = []
                    matches = x.xpath("(.//td[@class='label']//text())[position()<3]").extract()
                    match_join = '#'.join(matches)
                    match_replace1 = match_join.replace('#', '')
                    match_replace2 = match_replace1.replace(' vs ', '#')
                    match_list.append(match_replace2)
                    Home, Away = zip(*(s.split("#") for s in match_list))
                except:
                    pass

                home_c = str(Home) + str(country)
                home_c_rep = home_c.replace("'", '')
                home_c_rep = home_c_rep.replace('"', '')
                home_c_rep = home_c_rep.replace('(', '', 1)
                home_c_rep = home_c_rep.replace(')', '', 1)
                home_c_rep = home_c_rep.replace(',', '')
                home_c_rep = home_c_rep.replace('(', ' (', 1)

                away_c = str(Away) + str(country)
                away_c_rep = away_c.replace("'", '')
                away_c_rep = away_c_rep.replace('"', '')
                away_c_rep = away_c_rep.replace('(', '', 1)
                away_c_rep = away_c_rep.replace(')', '', 1)
                away_c_rep = away_c_rep.replace(',', '')
                away_c_rep = away_c_rep.replace('(', ' (', 1)                    

                try:
                    score_list = []
                    score = x.xpath("(.//td[@class='value'])[1]/text()").extract()
                    for z in score:
                        score1 = z.replace(')', '')
                        score_list.append(score1)
                    score_list2 = []
                    for w in score_list:
                        score2 = w.replace(' (', '#')
                        score_list2.append(score2)
                    FT, HT = zip(*(s.split("#") for s in score_list2))
                except:
                    pass
                FT1, FT2 = zip(*(s.split(":") for s in FT))
                HT1, HT2 = zip(*(s.split(":") for s in HT))

                m_time = x.xpath(".//td[@class='date']/text()").extract_first()
                m_time_replace = m_time.replace(' ', '#')
                m_time_split = m_time_replace.split('#')
                m_time_split2 = m_time_split[2]

                date_time = current_date + " " + m_time_split2
                date_time1 = datetime.datetime.strptime(date_time, '%Y-%B-%d %H:%M')


                  
                yield {
                    'country' : country,
                    'league': league,
                    'cl': cl_rep,
                    'home': Home,
                    'home_country': home_c_rep,
                    'away': Away,
                    'away_country' : away_c_rep,
                    'm_date': datetime_object,
                    'm_time' : m_time_split2,
                    'dt': date_time1,
                    'ft1' : FT1,
                    'ft2' : FT2,
                    'ht1': HT1,
                    'ht2': HT2
                }
# -*- coding: utf-8 -*-
import scrapy
import unicodedata
import re


class ResultSpider(scrapy.Spider):
    name = 'result'
    allowed_domains = ['see.ntc.net.np']
    start_urls = ['http://see.ntc.net.np/grade.php']

    #input file
    with open('input.csv','r') as f:
        data = f.read().split('\n')

    def parse(self, response):
        try:
            for i in range(len(self.data)):
                data_n=self.data[i].split(',')
                sym = data_n[0]
                dob = data_n[1]
                yield scrapy.FormRequest.from_response(
                response,
                formdata={'symbol': sym, 'dob': dob, 'submit': 'submit'},
                callback=self.parse_result
            )
        except:
            pass
    def parse_result(self, response):

        symbol_num = response.xpath('//*[@id="innerpan"]/div[5]/table/tr/td/table/tr[1]/td/div[2]//b')[0].xpath(
            './/text()').get(default='')
        dob = response.xpath('//*[@id="innerpan"]/div[5]/table/tr/td/table/tr[1]/td/div[2]//b')[1].xpath(
            './/text()').get(default='')
        exam_date = response.xpath('//*[@id="innerpan"]/div[5]/table/tr/td/table/tr[1]/td/div[2]//b')[2].xpath(
            './/text()').get(default='')
        score = []
        count = 0
        for subject in response.xpath('//*[@id="innerpan"]/div[5]/table/tr/td/table/tr[3]/following-sibling::tr'):
            try:
                subject_data = subject.xpath('.//td//text()').getall()
                subject_name = unicodedata.normalize("NFKD", subject_data[0]).strip().replace(' ','')
                if len(subject_name) == 0:
                    continue
                try:
                    grade_obtained = subject_data[4]
                    grade_point_obtained = subject_data[5]
                except:
                    grade_obtained = subject_data[3]
                    grade_point_obtained = subject_data[4]
                score.append(subject_name+' - '+ str(grade_point_obtained)+' ('+ str(grade_obtained)+')')
                count += 1
            except:
                break
        gpa = re.findall(r'\d+.\d+', response.xpath('.//b[contains(.,"GPA")]//text()').get(default=''))[0]

        yield {
            'symbol_number': symbol_num,
            'dob': dob,
            'exam_date': exam_date,
            'subject_score': ' | '.join(score),
            'GPA': gpa,
        }

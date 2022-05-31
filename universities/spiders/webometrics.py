import scrapy
#import csv

class webometrics(scrapy.Spider):
    name = "metrics"
    
    def start_requests(self):
        start_urls = [
            "https://webometrics.info/en/world"
            ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
#        regional_urls = [
#            "https://webometrics.info/en/Africa"
#            "https://webometrics.info/en/aw"
#            "https://webometrics.info/en/Asia"
#            "https://webometrics.info/en/Europe"
#            "https://webometrics.info/en/Latin_America"
#            "https://webometrics.info/en/North_america"
#            "https://webometrics.info/en/Oceania"
#            ]

    def parse(self, response):
        open("universities.csv", "w").write(("university,"
                                            "website,"
                                            "country,"
                                            "rank,"
                                            "impact_rank,"
                                            "openness_rank,"
                                            "excellence_rank,\n"))
        
#           csv.writer(open("universities.csv", "a")).writerow(row)

        rows = response.css("#block-system-main tr")
        uni_column = 2
        country_column = 4

#        Extract university name
        unis = rows.css(f"td:nth-child({uni_column})")
        unis = unis.extract()

#        Extract university url
        uni_urls = rows.css(f"td:nth-child({uni_column}) a::attr(href)")
        uni_urls = uni_urls.extract()

#        Extract Country
        countries = rows.css(f"td:nth-child({country_column}) img::attr(src)")
        countries = countries.extract()

        for i in range(len(rows) - 1):
            uni = unis[i].split(">")[2].split("<")[0]
            website = uni_urls[i]
            country = countries[i].split("/")[-1].split(".")[0].upper()
            self.log(uni)
            self.log(website)
            self.log(country)

#        Extract ranks
        for column in [1, 5, 6, 7]:
            ranks = rows.css(f"td:nth-child({column})").extract()
            for i in range(len(ranks)):
                pass
                #self.log(ranks[i].split(">")[2].split("<")[0])
   
           
        first_page = response.url.split("/")[-1]
        filename = f"data/metrics-{first_page}.html"
        with open(filename, "wb") as f:
            f.write(response.body)
        
        next_page = response.css("li.pager-next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)

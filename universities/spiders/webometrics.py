import scrapy
import csv
import pandas as pd

class webometrics(scrapy.Spider):
    name = "metrics"
    university = []


    def start_requests(self):
        start_urls = [
                    "https://webometrics.info/en/Africa",
                    "https://webometrics.info/en/aw",
                    "https://webometrics.info/en/Asia",
                    "https://webometrics.info/en/Europe",
                    "https://webometrics.info/en/Latin_America",
                    "https://webometrics.info/en/North_america",
                    "https://webometrics.info/en/Oceania" 
                    ]
        
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        path = "temp/universities-july.csv"
        save_path = "temp/universities-july.xlsx"
        
        open(path, "w").write(("university,"
                                            "website,"
                                            "country,"
                                            "region,"
                                            "world_rank,"
                                            "region_rank,"
                                            "impact_rank,"
                                            "openness_rank,"
                                            "excellence_rank,\n"))
        
        rows = response.css("#block-system-main tr")
        num_rows = len(rows) - 1
        uni_column = 3
        country_column = 5

#        Extract university name
        unis = rows.css(f"td:nth-child({uni_column})")
        unis = unis.extract()

#        Extract university url
        uni_urls = rows.css(f"td:nth-child({uni_column}) a::attr(href)")
        uni_urls = uni_urls.extract()

#        Extract country
        countries = rows.css(f"td:nth-child({country_column}) img::attr(src)")
        countries = countries.extract()
        
#        Extract region
        regions = response.css("h1#page-title::text")
        regions = regions.extract()[0]

        for i in range(num_rows):
            uni = unis[i].split(">")[2].split("<")[0]
            website = uni_urls[i]
            country = countries[i].split("/")[-1].split(".")[0].upper()
            rank_list = []

            for column in [2, 1, 6, 7, 8]:
#                Extract ranks
                ranks = rows.css(f"td:nth-child({column})").extract()
                rank_list.append(ranks[i].split(">")[2].split("<")[0])

            self.university.append([uni,
                                    website,
                                    country,
                                    regions,
                                    rank_list[0],
                                    rank_list[1],
                                    rank_list[2],
                                    rank_list[3],
                                    rank_list[4]])

        for i, row in enumerate(self.university):
            csv.writer(open(path, "a")).writerow(self.university[i])
            
        next_page = response.css("li.pager-next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)
            
        df = pd.read_csv(path)
        df.sort_values(by="world_rank", inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_excel(save_path, index=False)

from bs4 import BeautifulSoup as bs
from requests import Session

import pandas as pd

AO3_URL = "https://archiveofourown.org"
URL = "https://archiveofourown.org/works?commit=Sort+and+Filter&work_search%5Bsort_column%5D=kudos_count&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=T&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=en&tag_id=Lán+Zhàn+%7C+Lán+Wàngjī*s*Wèi+Yīng+%7C+Wèi+Wúxiàn"
NB_PAGES = 2

# Output titre, ratio, link, tags, rating


class Work:
    def __init__(self, content) -> None:
        self.content = content

        self.title = content.find("h4").a.contents[0]

        self.link = AO3_URL + content.find("h4").a["href"]

        stats = content.find("dl", {"class": "stats"})
        self.hits = int(stats.find("dd", {"class": "hits"}).contents[0])
        self.bookmarks = int(stats.find("dd", {"class": "bookmarks"}).a.contents[0])
        self.kudos = int(stats.find("dd", {"class": "kudos"}).a.contents[0])

        self.rating = (
            content.find("a", {"title": "Symbols key"}).span.contents[0].contents[0]
        )

        self.ratio_kudos = int((self.kudos / self.hits) * 100)  # TODO: best percentage
        self.ratio_bookmarks = int((self.bookmarks / self.hits) * 100)
        self.tags = self.get_tags()

    def get_info(self):
        return (
            self.title,
            self.ratio_kudos,
            self.ratio_bookmarks,
            self.link,
            self.tags,
            self.rating,
        )

    def get_tags(self):
        tags = self.content.find("ul", {"class": "tags commas"}).find_all("li")
        tags = [tag.contents[0].contents[0] for tag in tags]
        tags[0] = tags[0].contents[0]
        tags[1] = tags[1].contents[0]
        tags = ", ".join(tags)
        return tags


def get_page(base_url, page_number):
    a, b = base_url.split("Sort+and+Filter")
    return a + "Sort+and+Filter" + f"&page={page_number}" + b


if __name__ == "__main__":
    session = Session()
    infos = []
    for page in range(NB_PAGES):
        site = session.get(get_page(URL, page + 1))
        content = bs(site.content, "html.parser")
        works = content.find_all("li", {"role": "article"})
        for work in works:
            parsed_work = Work(work)
            infos.append(parsed_work.get_info())

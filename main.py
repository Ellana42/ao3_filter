import sys

from bs4 import BeautifulSoup as bs, NavigableString
import pandas as pd
from requests import Session

AO3_URL = "https://archiveofourown.org"

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
            self.title.replace(";", ","),
            self.ratio_kudos,
            self.ratio_bookmarks,
            self.link,
            self.tags.replace(";", ","),
            self.rating.replace(";", ","),
        )

    def get_tags(self):
        tags = self.content.find("ul", {"class": "tags commas"}).find_all("li")
        tags = [tag.contents[0].contents[0] for tag in tags]
        tags = [
            tag.contents[0] if type(tag) != NavigableString else tag for tag in tags
        ]
        tags = ", ".join(tags)
        return tags


def get_page(base_url, page_number):
    if "Sort+and+Filter" in base_url:
        a, b = base_url.split("Sort+and+Filter")
        return a + "Sort+and+Filter" + f"&page={page_number}" + b
    else:
        return base_url + f"?page={page_number}"


if __name__ == "__main__":
    url = "https://archiveofourown.org/works?commit=Sort+and+Filter&work_search%5Bsort_column%5D=kudos_count&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=T&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=en&tag_id=Lán+Zhàn+%7C+Lán+Wàngjī*s*Wèi+Yīng+%7C+Wèi+Wúxiàn"
    nb_pages = 1
    if len(sys.argv) == 2:
        url = sys.argv[1]
    if len(sys.argv) == 3:
        url = sys.argv[1]
        nb_pages = int(sys.argv[2])
    session = Session()
    infos = []
    for page in range(nb_pages):
        site = session.get(get_page(url, page + 1))
        content = bs(site.content, "html.parser")
        works = content.find_all("li", {"role": "article"})
        for work in works:
            parsed_work = Work(work)
            infos.append(parsed_work.get_info())
    dataframe = pd.DataFrame.from_records(
        infos,
        columns=["title", "ratio_kudos", "ratio_bookmarks", "link", "tags", "rating"],
    )
    dataframe.to_csv("works.csv", sep=";")

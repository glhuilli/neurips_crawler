import argparse
import json
import os
import re
import time
import uuid
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, TextIO

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

_BASE_URL = 'http://papers.nips.cc'
_CRAWLING_WAIT_TIME = 10
_NEURIPS_NAMESPACE = uuid.UUID('5ee6531f-0d79-4cf1-8da6-dc83cb553336')
_FIRST_YEAR = 1988
_PDF_FOLDER = 'pdfs'


class NeuripsUrl(NamedTuple):
    url: str
    year: str


class NeuripsPaper:
    def __init__(self, id_, title, pdf_name, pdf_link, info_link):
        self.id_: str = id_
        self.title: str = title
        self.pdf_name: str = pdf_name
        self.pdf_link: str = pdf_link
        self.info_link: str = info_link
        self.abstract: Optional[str] = None
        self.authors: Optional[List[Dict[str, str]]] = None


def crawl_papers(neurips_url: NeuripsUrl) -> Iterable[NeuripsPaper]:
    for link in get_paper_links(neurips_url.url):
        paper = init_neurips_paper(link)
        paper_soup = BeautifulSoup(requests.get(paper.info_link).content, 'lxml')
        get_abstract(paper, paper_soup)
        get_authors(paper, paper_soup)
        yield paper


def get_conference_links(year_from: int, year_to: int) -> Iterable[NeuripsUrl]:
    base = _BASE_URL + '/book/advances-in-neural-information-processing-systems-{}-{}'
    number_year_from = year_from - _FIRST_YEAR + 1
    number_year_to = year_to - _FIRST_YEAR + 1
    for idx, i in enumerate(range(number_year_from, number_year_to + 1)):
        year = str(year_from + idx)
        url = base.format(str(i), year)
        yield NeuripsUrl(url=url, year=year)


def save_pdf_file(pdf_link: str, pdf_name: str, year_output_folder: str) -> None:
    pdf = requests.get(pdf_link)
    with open(os.path.join(year_output_folder, _PDF_FOLDER, pdf_name), 'wb') as pdf_file:
        pdf_file.write(pdf.content)


def get_paper_links(url: str) -> Iterable[Any]:
    url_request = requests.get(url)
    for link in BeautifulSoup(url_request.content, 'lxml').find_all('a'):
        if link['href'][:7] == '/paper/':
            yield link


def init_neurips_paper(link: Any) -> NeuripsPaper:
    paper_title = link.contents[0]
    info_link = _BASE_URL + link['href']
    pdf_link = info_link + '.pdf'
    pdf_name = link['href'][7:] + '.pdf'
    paper_id = str(uuid.uuid5(_NEURIPS_NAMESPACE, re.findall(r'^(\d+)-', pdf_name)[0]))
    return NeuripsPaper(
        id_=paper_id, title=paper_title, info_link=info_link, pdf_link=pdf_link, pdf_name=pdf_name)


def get_abstract(paper: NeuripsPaper, paper_soup: Any) -> None:
    paper.abstract = paper_soup.find('p', attrs={'class': 'abstract'}).contents[0]


def get_authors(paper: NeuripsPaper, paper_soup: Any) -> None:
    paper_authors = [(re.findall(r'-(\d+)$', author.contents[0]['href'])[0],
                      author.contents[0].contents[0])
                     for author in paper_soup.find_all('li', attrs={'class': 'author'})]
    paper.authors = []
    for author in paper_authors:
        id_ = str(uuid.uuid5(_NEURIPS_NAMESPACE, author[0].lower()))
        paper.authors.append({'id': id_, 'name': author[1]})


def save_paper(paper: NeuripsPaper, output_folder: str, output: TextIO) -> None:
    save_pdf_file(paper.pdf_link, paper.pdf_name, output_folder)
    output.write(json.dumps(paper.__dict__) + '\n')


def parse_args():
    parser = argparse.ArgumentParser(description='Crawl NeurIPS Papers.')
    parser.add_argument('--from_year', help='Starting year to crawl')
    parser.add_argument('--to_year', help='Final year to crawl')
    parser.add_argument('--output', default='./output/', help='Output classifier path')
    return parser.parse_args()


def main(args):
    for neurips_url in tqdm(
            get_conference_links(int(args.from_year), int(args.to_year)),
            'iterating over conferences'):
        year_output_folder = os.path.join(args.output, f'data_{neurips_url.year}')
        if os.path.isdir(year_output_folder):
            continue
        os.makedirs(f'{year_output_folder}/{_PDF_FOLDER}')
        with open(os.path.join(year_output_folder, 'papers_data.jsons'), 'w') as output:
            for paper in tqdm(crawl_papers(neurips_url), 'iterating over papers'):
                try:
                    save_paper(paper, year_output_folder, output)
                except TypeError:
                    continue
        time.sleep(_CRAWLING_WAIT_TIME)


if __name__ == '__main__':
    main(parse_args())

import requests
from bs4 import BeautifulSoup, Tag


def scrape():

    url = "https://www.nytimes.com/games/wordle/index.html"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())
    print(soup.get_text())
    print()

    board_class = "Board-module_board__jeoPS"

    # title = soup.select_one(board_class)

    # print(soup.find(id='div'))

    # print(soup.find_all("div"))
    # content: Tag = soup.select_one("ratio-hook")
    # print(content)
    
    text = soup.select_one('h2')
    print(text)

    # link = soup.select_one('a').get('href')

    # print(link)


if __name__ == '__main__':
    scrape()
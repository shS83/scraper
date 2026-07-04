import requests
from bs4 import BeautifulSoup
from typing import Any
import re
from urllib.parse import urlsplit, urljoin
from datetime import datetime

all_tables = []
comics = []
FINGERPORI_API_URL = (
	"https://www.hs.fi/api/laneitems/"
	"39221/list/normal/290"
	"?listTemplate=teaser-m"
)

FINGERPORI_PAGE_URL = (
	"https://www.hs.fi/sarjakuvat/fingerpori/"
)


def iter_dicts(value: Any):
	if isinstance(value, dict):
		yield value

		for child in value.values():
			yield from iter_dicts(child)

	elif isinstance(value, list):
		for child in value:
			yield from iter_dicts(child)


def get_latest_fingerpori() -> tuple[str, str] | None:
	headers = {
		"Accept": "application/json",
		"Referer": FINGERPORI_PAGE_URL,
		"User-Agent": (
			"Mozilla/5.0 (X11; Linux x86_64; rv:153.0) "
			"Gecko/20100101 Firefox/153.0"
		),
	}

	response = requests.get(
		FINGERPORI_API_URL,
		headers=headers,
		timeout=30,
	)

	response.raise_for_status()
	data = response.json()

	fingerporis = []

	for item in iter_dicts(data):
		if item.get("resourceType") != "Cartoon":
			continue

		if item.get("title") != "Fingerpori":
			continue

		picture = item.get("picture")

		if not isinstance(picture, dict):
			continue

		if not item.get("href") or not picture.get("url"):
			continue

		fingerporis.append(item)

	if not fingerporis:
		print("Fingerpori API returned no cartoons.")
		return None

	latest = max(
		fingerporis,
		key=lambda item: (
			datetime.fromisoformat(item["displayDate"]),
			int(item["id"]),
		),
	)

	article_url = urljoin(
		FINGERPORI_PAGE_URL,
		latest["href"],
	)

	image_url = (
		latest["picture"]["url"]
		.replace("WIDTH", "978")
		.replace("EXT", "webp")
	)

	print(
		f'Latest Fingerpori: {latest["displayDate"]}'
	)

	print(
		f"Fingerpori article: {article_url}"
	)

	print(
		f"Fingerpori image: {image_url}"
	)

	return article_url, image_url

def scrape(url: str):
    domain = urlsplit(url).netloc
    to_return = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    status = response.status_code
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    print(f"Scraping: {soup.title.get_text()}")
    print("Site status OK" if status == 200 else f"ERROR {status}")

    if "yle" in domain:
        scraped = soup.find_all("a", class_=re.compile("underlay-link"))
        for s in scraped:
            data_line = {"title": s.get_text(), "href": s["href"]}
            if data_line not in to_return:
                to_return.append(data_line)

    elif "iltalehti" in domain:
        full = soup.find("div", class_="full-article")
        head_full = full.find_next("div", class_="front-title")
        fullhref = full.find_next("a")
        data_line = {"title": head_full.get_text(), "href": fullhref["href"]}
        if data_line not in to_return:
            to_return.append(data_line)
        halves = soup.find_all("a", class_="half-article-content")

        for h in halves:
            halfhead = h.find_next("div", class_="front-title")
            data_line = {"title": halfhead.get_text(), "href": h["href"]}
            if data_line not in to_return:
                to_return.append(data_line)

    elif "pelaaja" in domain:
        scraped = soup.find_all("a", class_="block")
        for s in scraped:
            ugly = s.get_text().strip().split("\n")
            if "image/svg+xml" in ugly[0] or "Episodi.fi" in ugly[0]:
                continue
            prettier = ugly[0].replace("Uutinen | ", "")
            data_line = {"title": prettier, "href": s["href"]}
            if data_line not in to_return:
                to_return.append(data_line)

    elif "tomshardware" in domain:
        scraped = soup.find_all("a", class_="article-link")
        for s in scraped:
            ugly = s.get_text().strip().split("\n")
            data_line = {"title": ugly[0], "href": s["href"]}
            if data_line not in to_return:
                to_return.append(data_line)

    elif "mikrobitti" in domain:
        cards = soup.select(
            "#main-content .full-article, "
            "#main-content .thin-article, "
            "#main-content .half-article"
        )

        seen_urls = set()

        print(f"Mikrobitti: found {len(cards)} article cards")

        for card in cards:
            link = card.find("a", href=True)

            if link is None:
                continue

            title_element = card.select_one(".front-title")

            if title_element is not None:
                title = title_element.get_text(" ", strip=True)
            else:
                # Varakeino, jos front-title joskus taas muuttuu.
                title = link.get_text(" ", strip=True)

            address = urljoin(url, link["href"])

            if not title or address in seen_urls:
                continue

            seen_urls.add(address)

            to_return.append(
                {
                    "title": title,
                    "href": address,
                }
            )

    elif "muropaketti" in domain:
        heads = soup.find_all("h3", class_=re.compile("box-item__headline"))

        for s in heads:
            item = s.find_next("a", href=re.compile("muropaketti"))
            data_line = {"title": item.get_text(), "href": item["href"]}
            if data_line not in to_return:
                to_return.append(data_line)

    else:
        return False

    domain_split = domain.split(".")

    if "www" in domain_split:
        d_name = domain_split[1]
    else:
        d_name = domain_split[0]

    generated_table = generate_table_html(to_return, f"https://{domain}", d_name)

    return generated_table


def get_comic(url: str):
    domain = urlsplit(url).netloc
    comic = False
    response = requests.get(url)
    status = response.status_code
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    print(f"Scraping: {soup.title.get_text()}")
    print("Site status OK" if status == 200 else "ERROR")

    if "hs.fi" in domain:
        result = get_latest_fingerpori()

        if result is None:
            return False

        article_url, comic = result

    if "smbc" in url:
        scraped = soup.find("img", id=re.compile("cc-comic"))
        comic = scraped["src"]

    if "xkcd" in url:
        scraped = soup.find("div", id=re.compile("comic"))
        img = scraped.find_next("img")
        comic = f'http:{img["src"]}'

    if "oglaf" in url:
        scraped = soup.find("img", id=re.compile("strip"))
        comic = scraped["src"]

    if not comic:
        print(f"Comic image not found: {url}")
        return False

    domain_split = domain.split(".")

    if "www" in domain_split:
        d_name = domain_split[1]
    else:
        d_name = domain_split[0]

    comic_table = comics_to_tables(comic, f"https://{domain}", d_name)

    return comic_table


def generate_table_html(scraped_list: list, url_prefix: str, domain: str):
    global all_tables

    table_html = [
        f'<table class="taulu" id="taulu{len(all_tables)}">',
        f"<caption>{domain.upper()} Headlines</caption>",
    ]
    for item in scraped_list:
        gradient = "background: #323263;"
        t_s = f'<tr><td style="{gradient}">'
        t_e = "</td></tr>"
        h_text = item["title"].replace("­", "")
        if domain in item["href"]:
            address = item["href"]
        else:
            address = urljoin(f"{url_prefix}/", item["href"])
        anchor = f'<a href="{address}">{h_text}</a>'
        table_html.append(f"{t_s}{anchor}{t_e}\n")

    table_html.append("</table>")
    return table_html


def comics_to_tables(comic: str, url_prefix: str, domain: str):
    global all_tables, comics
    title = domain.upper()
    if title == "HS":
        title = "FINGERPORI"

    table_html = [
        f'<table class="taulu" id="taulu{len(all_tables) + len(comics)}">',
        f"<caption>{title}</caption>",
    ]
    t_s = "<tr><td>"
    t_e = "</td></tr>"
    anchor = f'<a href="{comic}"><img src="{comic}" alt="comic" /></a>'
    table_html.append(f"{t_s}{anchor}{t_e}\n")
    table_html.append("</table>")
    return table_html


def generate_page(tables_list: list):
    output_start = """<!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <title>Headlines</title>
        <link rel="stylesheet" href="mock_style.css"/>
    </head>
    <body>
    <div class="bg-image">
    </div>
    """

    nav_start = '<nav class="navbar">\n'
    nav_end = "</nav>\n"

    output_start += nav_start

    for x, v in enumerate(tables_list):
        provider = v[1].split(" ")[0].replace("<caption>", "").lower()
        provider = provider[0].upper() + provider[1:]
        output_start += f'<button class="button after" type="button" onClick="change_{x}()">{provider}</button>\n'

    output_start += nav_end
    output_start += '<div id="container">\n'
    output_start += f"<p>updated {datetime.now()}</p>\n"
    output_end = """
    </div>
    </body>
    </html>
    """

    print("Prettifying...")
    actual_output = output_start

    for table in tables_list:
        for row in table:
            actual_output += row

    # Add JS

    script_start = '<script type="text/javascript">'
    script_end = "</script>"

    actual_output += script_start

    for x, value in enumerate(tables_list):
        script_to_add = "function change_" + str(x) + "() {\n"
        script_to_add += f'        let x = document.getElementById("taulu{x}");\n'
        script_to_add += '        if (x.style.display === "none") {\n'
        script_to_add += '            x.style.display = "";\n'
        script_to_add += "        } else {\n"
        script_to_add += '            x.style.display = "none";\n'
        script_to_add += "        }\n"
        script_to_add += "    }\n"
        actual_output += str(script_to_add)

    actual_output += script_end

    # End Add JS

    actual_output += output_end
    soppa = BeautifulSoup(actual_output, features="html.parser")
    prettier_soppa = soppa.prettify()

    print("Saving to file...")

    with open("./cache.html", "w", encoding="utf-8") as f:
        f.write(prettier_soppa)
    f.close()

    print("Done.")
    return True


def execute():
    global all_tables, comics

    urls = [
        "https://yle.fi/",
        "https://www.iltalehti.fi/uutiset",
        "https://www.pelaaja.fi/uutiset",
        "https://muropaketti.com/",
        "https://www.tomshardware.com/",
        "https://www.mikrobitti.fi/",
    ]

    for url in urls:
        try:
            table = scrape(url)
        except Exception as error:
            print(
                f"Error scraping {url}: "
                f"{type(error).__name__}: {error}"
            )
            continue

        if table:
            all_tables.append(table)
        else:
            print(f"Skipping unsupported or failed source: {url}")

    comic_urls = [
        "https://www.hs.fi/sarjakuvat/fingerpori/",
        "https://www.smbc-comics.com/",
        "https://xkcd.com/",
        "https://www.oglaf.com/",
    ]

    for url in comic_urls:
        try:
            table = get_comic(url)
        except Exception as error:
            print(
                f"Error scraping comic {url}: "
                f"{type(error).__name__}: {error}"
            )
            continue

        if table:
            comics.append(table)
        else:
            print(f"Skipping failed comic: {url}")

    all_tables.extend(comics)

    if not all_tables:
        print("No tables were generated.")
        return False

    generate_page(all_tables)
    return True


if __name__ == "__main__":
    raise SystemExit(0 if execute() else 1)

import requests
import os
import re
import csv

#####################################################################
# ZAJEM PODATKOV O KNJIGAH
#####################################################################

goodreads_webpage = "https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once"
goodreads_directory = 'goodreads-data'
csv_filename = 'goodreads.csv'

#####################################################################
# Extracting data from the webpage
#####################################################################

def download_url_to_string(url):
    try:
        page_content = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Internet disconnected!')
        return None
    return page_content.text

def save_string_to_file(text, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)
    return None

def save_pages():
    for page_number in range(57, 101):
        url = goodreads_webpage + f'?page={page_number}'
        filename = f'goodreads-knjige-na-strani-{page_number}'
        webpage_content = download_url_to_string(url)
        save_string_to_file(webpage_content, goodreads_directory, filename)

#####################################################################
# Processing the data
#####################################################################

def read_file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

# Funkcija, ki vrne vsebino spletne strani razdeljeno na knjige, kot seznam

def page_to_books(page_content):
    pattern = r'<tr itemscope itemtype="http://schema.org/Book">(.*?)</tr>'
    regexp = re.compile(pattern, re.DOTALL)
    return re.findall(regexp, page_content)

# Funkcija, ki iz niza potegne ven podatke o naslovu knjige, imenu avtorja, 
# oceni, letu izdaje, povprecni oceni, stevilu strani.

def get_dict_from_book(book_block):
    regexp = re.compile(
        r"<span itemprop='name' role='heading'.*?>(?P<title>.*?)</span>.*?"
        r'<a class="authorName".*><span itemprop="name">(?P<author>.*?)</span></a>.*?'
        r'<span class="minirating">.*</span></span> (?P<average_rating>.*?) avg rating &mdash; (?P<ratings>.*) ratings</span>.*?'
        r'return false;">score: (?P<score>.*?)</a>', 
        flags=re.DOTALL
    )
    hit = re.search(regexp, book_block)
    if hit == None:
        book = {}
    else:
        book = hit.groupdict()
        book['average_rating'] = float(book['average_rating'].strip())
        book['ratings'] = int(book['ratings'].replace(',', '').strip())
        book['score'] = int(book['score'].replace(',', '').strip())
    return book

def books_on_page(page_number):
    filename = f'goodreads-knjige-na-strani-{page_number}'
    content = read_file_to_string(goodreads_directory, filename)
    for book_block in page_to_books(content):
        yield get_dict_from_book(book_block)

#####################################################################
# Saving the processed data in CSV file
#####################################################################    

def write_csv(dicts, field_names, filename):
    os.makedirs("goodreads-processed-data", exist_ok=True)
    path = os.path.join("goodreads-processed-data", filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in dicts:
            writer.writerow(dict)

#####################################################################
#####################################################################

def main():
    # save_pages()
    books = []
    for page_number in range(1, 101):
        for book in books_on_page(page_number):
            books.append(book)
    write_csv(
        books,
        ['title', 'author', 'average_rating', 'ratings', 'score'],
        csv_filename
    )

if __name__ == '__main__':
    main()
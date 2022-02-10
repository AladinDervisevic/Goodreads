import requests
import os
import re
import csv

#####################################################################
# ZAJEM PODATKOV O KNJIGAH
#####################################################################

goodreads_webpage = "https://www.goodreads.com"
goodreads_directory = 'goodreads-data'
books_directory = 'books-data'
csv_filename = 'goodreads.csv'
csv_filename2 = 'goodreads2.csv'

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

def read_file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def save_pages():
    for page_number in range(1, 101):
        url = goodreads_webpage + f'/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once?page={page_number}'
        filename = f'goodreads-knjige-na-strani-{page_number}'
        webpage_content = download_url_to_string(url)
        save_string_to_file(webpage_content, goodreads_directory, filename)

def save_book_pages():
    titles_string = read_file_to_string(books_directory, "book-filenames.txt")
    for title in titles_string.split('/n'):
        url = goodreads_webpage + f'/book/show/{title}'
        filename = f'book-{title}'
        webpage_content = download_url_to_string(url)
        save_string_to_file(webpage_content, books_directory, filename)

#####################################################################
# Processing the data
#####################################################################

# funkcija, ki vrne povezave do posameznih knjig kot seznam stringov 

def get_title_links(page_content):
    pattern = r'<a class="bookTitle" itemprop="url" href="/book/show/(.*?)">.*?<span'
    regexp = re.compile(pattern, re.DOTALL)
    return re.findall(regexp, page_content)

# Funkcija, ki iz niza potegne ven podatke o naslovu knjige, imenu avtorja, 
# povprecni oceni, letu izdaje, stevilu strani.
    
def get_dict_from_book(book_block):
    regexp = re.compile(
        r'<h1 id="bookTitle" .*? itemprop="name">\s*(?P<title>.*?)\s*</h1>.*?'
        r'<a class="authorName" .*><span itemprop="name">(?P<author>.*?)</span></a>.*?'
        r'<span itemprop="ratingValue">\s*(?P<average_rating>.*?)\s*</span>.*?'
        r'<meta itemprop="ratingCount" .*? />\s*(?P<ratings>.*?)\s*ratings.*?'
        r'<span itemprop="numberOfPages">\s*?(?P<pages>\d+)\s*pages</span>.*?'
        r'<div class="row">\s*Published\s*.*?\s.*?\s(?P<date>\d\d\d\d).*?</div>', 
        flags=re.DOTALL
    )
    hit = re.search(regexp, book_block)
    if hit == None:
        book = {}
    else:
        book = hit.groupdict()
        book['average_rating'] = float(book['average_rating'].strip())
        book['ratings'] = int(book['ratings'].replace(',', '').strip())
        book['pages'] = int(book['pages'].replace(',', '').strip())
        book['date'] = int(book['date'].strip())
    return book

def dicts_books():
    titles = read_file_to_string(books_directory, "book-filenames.txt").split("/n")
    for title in titles:
        filename = f'book-{title}'
        content = read_file_to_string(books_directory, filename)
        yield get_dict_from_book(content)

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

    # book_names = []
    # for page_number in range(1, 101):
    #     filename = f'goodreads-knjige-na-strani-{page_number}'
    #     content = read_file_to_string(goodreads_directory, filename)
    #     book_names += get_title_links(content)
    # book_names = '/n'.join(book_names)
    # save_string_to_file(book_names, books_directory, "book-filenames.txt")
    # save_book_pages()

    books = [i for i in dicts_books()]
    write_csv(
        books,
        ['title', 'author', 'average_rating', 'ratings', 'pages', 'date'],
        csv_filename2,
    )

if __name__ == '__main__':
    main()
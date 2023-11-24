import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

url = 'https://books.toscrape.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
books = soup.select('section > div:nth-child(2) > ol > li > article')

books_data = []
for book in books:
    title = book.select_one('h3 > a')['title']
    book_url = book.select_one('h3 > a')['href']
    price = book.select_one('.product_price .price_color').text
    status = book.select_one('.product_price .instock.availability').text.strip()
    
    books_data.append({
        'title': title,
        'book_url': url + book_url,
        'price': price,
        'status': status,
    })

Base = declarative_base()
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    price = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    book_url = Column(String(100), nullable=False)

engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

for book_data in books_data:
    book = Book(title=book_data['title'], price=book_data['price'], status=book_data['status'], book_url=book_data['book_url'])
    session.add(book)

session.commit()
session.close()
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL сайта, с которого мы будем парсить данные
url = 'https://books.toscrape.com/'

# Запрос к сайту
response = requests.get(url)

# Парсинг HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Находим элементы книг
books = soup.select('section > div:nth-child(2) > ol > li > article')

# Собираем информацию о каждой книге
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

# # Выводим результат
# for book in books_data:
#     print(book)
    
# Определение базового класса модели
Base = declarative_base()

# Определение модели книги
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    price = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    book_url = Column(String(100), nullable=False)

# Создание соединения с базой данных
engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Добавление данных о книгах в базу данных
for book_data in books_data:
    book = Book(title=book_data['title'], price=book_data['price'], status=book_data['status'], book_url=book_data['book_url'])
    session.add(book)

# Фиксация транзакции
session.commit()

# Закрытие сессии
session.close()
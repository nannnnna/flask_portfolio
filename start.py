import requests

from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
from parsing import Book
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
import stripe
from flask import Flask, render_template, session, redirect, url_for

engine = create_engine('sqlite:///books.db')

app = Flask(__name__)

# Устанавливаем ключи для Stripe
stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'

app = Flask(__name__)
app.secret_key = 'sk_test_51NsTBiF6oMer2mpJqJr6mXh8S7GiJLXsPzRXgiVbFnMqxHVrPiBgiQzpZRwmhXNQ14lM7Scia0c4GddMZk0HYfxX0036Nvr5fy' # Нужно для работы сессий



@app.route('/create-checkout-session', methods=['GET'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Название книги',
                        },
                        'unit_amount': 2000, # Цена в центах
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/books')
def books():
    sort_order = request.args.get('sort', 'price_asc')
    in_stock = request.args.get('in_stock', '0')
    
    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Создание запроса к базе данных с учетом параметров сортировки и фильтрации
    query = session.query(Book)
    if in_stock == '1':
        query = query.filter(Book.status == 'In stock')
    if sort_order == 'price_asc':
        query = query.order_by(Book.price.asc())
    elif sort_order == 'price_desc':
        query = query.order_by(Book.price.desc())

    books = query.all()


    # Закрытие сессии
    session.close()

    return render_template('parse_book.html', books=books)


if __name__ == '__main__':
    app.run(debug=True)

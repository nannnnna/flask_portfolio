import stripe 

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy.orm import sessionmaker
from parsing import Book
from sqlalchemy import create_engine
from parsing import Base
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'sk_test_51NsTBiF6oMer2mpJqJr6mXh8S7GiJLXsPzRXgiVbFnMqxHVrPiBgiQzpZRwmhXNQ14lM7Scia0c4GddMZk0HYfxX0036Nvr5fy'
engine = create_engine('sqlite:///books.db')
stripe.api_key = 'sk_test_51NsTBiF6oMer2mpJqJr6mXh8S7GiJLXsPzRXgiVbFnMqxHVrPiBgiQzpZRwmhXNQ14lM7Scia0c4GddMZk0HYfxX0036Nvr5fy'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/books')
def books():
    sort_order = request.args.get('sort', 'price_asc')
    in_stock = request.args.get('in_stock', '0')
    
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(Book)
    if in_stock == '1':
        query = query.filter(Book.status == 'In stock')
    if sort_order == 'price_asc':
        query = query.order_by(Book.price.asc())
    elif sort_order == 'price_desc':
        query = query.order_by(Book.price.desc())

    books = query.all()

    session.close()

    return render_template('parse_book.html', books=books)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    book_id = request.form.get('book_id')
    book_title = request.form.get('book_title')
    price = request.form.get('price')
    clean_price = ''.join(filter(lambda x: x.isdigit() or x == '.', price))

    try:
        price = float(clean_price)   # Преобразовываем в число и переводим в центы
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book_title,
                    },
                    'unit_amount': int(float(price) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except ValueError:
        # Обработка ошибки, если цена не может быть преобразована в float
        return "Invalid price format"
    except Exception as e:
        return str(e)

@app.route('/success')
def success():
    # Обработка успешного платежа
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    # Обработка отмененного платежа
    return render_template('cancel.html')


if __name__ == '__main__':
    app.run(debug=True)

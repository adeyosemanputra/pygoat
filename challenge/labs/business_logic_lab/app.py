from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import uuid

app = Flask(__name__)
app.secret_key = 'business_logic_secret_key_2024'

PRODUCTS = [
    {'id': 1, 'name': 'Smartphone', 'price': 500, 'image': '📱'},
    {'id': 2, 'name': 'Laptop', 'price': 800, 'image': '💻'},
    {'id': 3, 'name': 'Headphones', 'price': 200, 'image': '🎧'},
]

COUPONS = {
    'DISCOUNT10': {
        'description': '10% off your order',
        'discount_percent': 10,
        'min_amount': 0
    },
    'SAVE20': {
        'description': '20% off orders over ₹500',
        'discount_percent': 20,
        'min_amount': 500
    }
}

def init_session():
    """Initialize session data if not present"""
    if 'cart' not in session:
        session['cart'] = []
    if 'order_id' not in session:
        session['order_id'] = str(uuid.uuid4())
    if 'applied_coupons' not in session:
        session['applied_coupons'] = []
    if 'secure_mode' not in session:
        session['secure_mode'] = False

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/store')
def store():
    init_session()
    return render_template('store.html', products=PRODUCTS)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    init_session()
    
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        cart_item = next((item for item in session['cart'] if item['id'] == product_id), None)
        if cart_item:
            cart_item['quantity'] += 1
        else:
            session['cart'].append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            })
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    init_session()
    
    cart_total = sum(item['price'] * item['quantity'] for item in session['cart'])
    
    discount_amount = 0
    for coupon_code in session['applied_coupons']:
        if coupon_code in COUPONS:
            coupon = COUPONS[coupon_code]
            if cart_total >= coupon['min_amount']:
                discount_amount += (cart_total * coupon['discount_percent']) / 100
    
    final_total = max(0, cart_total - discount_amount)
    
    return render_template('cart.html', 
                         cart=session['cart'],
                         cart_total=cart_total,
                         discount_amount=discount_amount,
                         final_total=final_total,
                         applied_coupons=session['applied_coupons'],
                         coupons=COUPONS,
                         secure_mode=session.get('secure_mode', False))

@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    init_session()
    
    coupon_code = request.form.get('coupon_code', '').strip().upper()
    
    if coupon_code in COUPONS:
        if session.get('secure_mode', False):
            if coupon_code not in session['applied_coupons']:
                session['applied_coupons'].append(coupon_code)
                session.modified = True
                return jsonify({
                    'success': True, 
                    'message': f'Coupon {coupon_code} applied successfully!',
                    'applied_coupons': session['applied_coupons']
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': f'Coupon {coupon_code} has already been applied to this order.',
                    'applied_coupons': session['applied_coupons']
                })
        else:
            session['applied_coupons'].append(coupon_code)
            session.modified = True
            return jsonify({
                'success': True, 
                'message': f'Coupon {coupon_code} applied successfully!',
                'applied_coupons': session['applied_coupons']
            })
    else:
        return jsonify({
            'success': False, 
            'message': 'Invalid coupon code. Try DISCOUNT10 or SAVE20.',
            'applied_coupons': session['applied_coupons']
        })

@app.route('/remove_coupon/<coupon_code>')
def remove_coupon(coupon_code):
    init_session()
    
    if coupon_code in session['applied_coupons']:
        session['applied_coupons'] = [c for c in session['applied_coupons'] if c != coupon_code]
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    session['applied_coupons'] = []
    session['order_id'] = str(uuid.uuid4())
    session.modified = True
    return redirect(url_for('store'))

@app.route('/toggle_secure_mode')
def toggle_secure_mode():
    init_session()
    session['secure_mode'] = not session.get('secure_mode', False)
    session.modified = True
    
    session['applied_coupons'] = []
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/lab')
def lab():
    init_session()
    return render_template('lab.html')

@app.route('/solution')
def solution():
    init_session()
    return render_template('solution.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
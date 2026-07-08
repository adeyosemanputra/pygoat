from decimal import Decimal
import traceback

from flask import Flask, render_template, request

app = Flask(__name__)

COUPON_RATES = {
    "SAVE10": Decimal("0.10"),
    "VIP25": Decimal("0.25"),
    "BETA05": Decimal("0.05"),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lab', methods=['GET', 'POST'])
def lab():
    result = None
    error = None
    error_details = None
    inputs = {
        "order_total": "",
        "divisor": "",
        "coupon": "",
    }

    if request.method == 'POST':
        inputs["order_total"] = request.form.get("order_total", "")
        inputs["divisor"] = request.form.get("divisor", "")
        inputs["coupon"] = request.form.get("coupon", "")

        try:
            order_total = Decimal(inputs["order_total"])
            divisor = Decimal(inputs["divisor"])
            coupon = inputs["coupon"].strip().upper()

            discount_rate = COUPON_RATES[coupon]
            discount_amount = order_total / divisor
            final_total = order_total - (discount_amount * discount_rate)

            result = f"${final_total:.2f}"
        except Exception:
            error = "Calculation failed due to an unexpected error."
            error_details = traceback.format_exc()

    return render_template(
        'lab.html',
        result=result,
        error=error,
        error_details=error_details,
        inputs=inputs,
        coupons=sorted(COUPON_RATES.keys()),
    )

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5016, debug=True)

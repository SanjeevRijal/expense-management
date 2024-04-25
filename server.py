from flask import request, jsonify, redirect
from model import User,Bill,Split
from config import app,db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta, datetime
from calculation import bill_detail,bill_share_with
import secrets
from send_email import send_password_reset_email


@app.route("/register", methods= ["POST"])
def register():
    register_data = request.get_json()
    form_email = register_data["email"]
    form_name = register_data["name"]
    form_password = register_data["password"]
    query = User.query.filter(User.email == form_email).scalar()
    if query:
        return "", 409
    else:
        new_user = User(
            email=form_email.lower(),
            password=generate_password_hash(form_password, method='pbkdf2', salt_length=16),
            name=form_name
        )
        db.session.add(new_user)
        db.session.commit()

    return "", 200


@app.route('/login', methods=["POST"])
def login():
    login_form_data = request.get_json()
    print("hi")
    print(login_form_data)
    result = User.query.filter_by(email = login_form_data["userName"].lower()).first()
    if result and check_password_hash(result.password, login_form_data["password"]):
        user_data = {
            "name":result.name,
        }
        access_token = create_access_token(identity=result.id)
        return jsonify(user_info = user_data , access_token=access_token,)
    return " or password", 500


@app.route("/refresh_token", methods=["POST"])
@jwt_required()
def refresh_token():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return {"access_token": new_token}, 200


@app.route("/user")
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    users = User.query.filter(User.id != current_user).all()
    users_list = []
    for user in users:
        users_list.append({"userId": user.id, "name": user.name, f"shareWith{user.name}": False})
    return jsonify({'user': users_list})

@app.route("/user_name")
@jwt_required()
def user_name():
    current_user = get_jwt_identity()
    user= User.query.filter(User.id == current_user).first()
    return user.name

@app.route("/my_bill")
@jwt_required()
def get_my_bill():
    current_user = get_jwt_identity()
    my_bills = Bill.query.filter_by(spender_id = current_user).all()
    my_bills_list = []
    for my_bill in my_bills:
        date_str = my_bill.spend_date.strftime('%Y-%m-%d')
        my_bills_list.append({"billId":my_bill.id, "amount":my_bill.amount, "catagory": my_bill.spend_type,
                              "spend_date":date_str})
    return {"myBill":my_bills_list}


@app.route("/all_bill")
def get_all_bill():
    all_bills = Bill.query.all()
    all_bills_list = []
    for all_bill in all_bills:
        date_str = all_bill.spend_date.strftime('%Y-%m-%d')
        all_bills_list.append({ "amount":all_bill.amount, "catagory": all_bill.spend_type,
                              "spend_date":date_str,"spenderName":all_bill.what_amount.name})
    return {"allBill":all_bills_list}

@app.route("/add_bill", methods=["POST"])
@jwt_required()
def add_bill():
    current_user = get_jwt_identity()
    new_bill_data = request.get_json()
    bill_data = new_bill_data["formData"]
    share_with = new_bill_data["checkBox"]

    new_bill = Bill(
        amount=bill_data["amount"],
        spend_type=bill_data["billType"],
        spend_date=datetime.now(),
        spender_id=current_user,
    )

    db.session.add(new_bill)
    db.session.commit()

    last_bill = Bill.query.filter(Bill.spender_id == current_user).order_by(Bill.id.desc()).first()
    last_bill_id = last_bill.id

    my_share = Split(
        split_with=current_user,
        bill_id=last_bill_id,
    )
    db.session.add(my_share)
    db.session.commit()

    for each_user in share_with:
        if each_user["shareWith"+each_user["name"]]:
            split_with = Split(
                split_with=each_user["userId"],
                bill_id=last_bill_id,
            )
            db.session.add(split_with)
            db.session.commit()
    return "Success", 200


@app.route("/delete_bill", methods=["POST"])
@jwt_required()
def delete_bill():
    to_delete_bill = request.get_json()
    bill = Bill.query.filter_by(id=to_delete_bill["bill_id"]).first()
    splits = bill.who_pay
    for split in splits:
        db.session.delete(split)
        db.session.commit()
    db.session.delete(bill)
    db.session.commit()
    return "i", 200


@app.route("/payment_details")
@jwt_required()
def final_payment():
    payment_calculation = {}
    each_person_to_pay = bill_share_with()
    each_person_spend = bill_detail()

    for spender_name, spend_amount in each_person_spend.items():
        for payer_name, amount_to_pay in each_person_to_pay.items():
            if spender_name == payer_name:
                payment_calculation[payer_name]= spend_amount-amount_to_pay
            elif payer_name not in payment_calculation:
                payment_calculation[payer_name] = -amount_to_pay

    final_payment_details = [{"name": keys, "amount": "%.2f" % value} for keys, value in payment_calculation.items()]

    return final_payment_details

@app.route("/validate_email" , methods = ["POST"])
def send_email_link():
    user_email = request.get_json()["email"]
    user = User.query.filter_by(email=user_email.lower()).first()
    if user:
        user.reset_token = secrets.token_urlsafe(30)
        user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        send_password_reset_email(user)
        return "Check email for further instruction ", 200
    return "No user Name", 400


@app.route("/reset_password/<token>", methods = ["GET"])
def verify_token(token):
    user = User.query.filter_by(reset_token=token).filter(User.reset_token_expiration > datetime.utcnow()).first()
    if not user:
        return "Invalid or expired reset token", 400
    return redirect(f"http://localhost:5173/password_update/{user.reset_token}", code=302)

@app.route("/conform_token", methods = ["POST"])
def conform_token():
    user_token = request.get_json()["token"]
    token_requests = User.query.filter_by(reset_token = user_token).first()
    if user_token == token_requests.reset_token:
        return {"message":"token conformed"}, 200
    return {"error":"someting went wrong"}, 400


@app.route("/update_password", methods =["POST"])
def update_password():
    response = request.get_json()
    user_token = response["token"]
    new_password = response["formData"]["password"]
    password_to_update_user = User.query.filter_by(reset_token=user_token).first()
    if password_to_update_user:
        hashed_password = generate_password_hash(new_password, method='pbkdf2', salt_length=16)
        password_to_update_user.password = hashed_password
        password_to_update_user.reset_token = None
        password_to_update_user.reset_token_expiration = None
        db.session.commit()
        return{"message":"Successfully changed"},200
    return {"error":"Something went wrong"}, 400


@app.route("/chart_data")
@jwt_required()
def chart_data():
    return bill_detail()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


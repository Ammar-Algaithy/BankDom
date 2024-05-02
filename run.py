from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, make_response
from app.models.user import User

app = Flask(__name__, template_folder='app/templates')
app.secret_key = 'your_secret_key_here'



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    user1 = None
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        user_name = request.form.get('userName')
        password = request.form.get('password')
        account_type = request.form.get('accountType')
        balance = request.form.get('balance')
        user1 = User(
            customer_user_name= user_name,
            customer_first_name= first_name,
            customer_last_name= last_name,
            customer_email= email,
            customer_password= password,
            account_type= account_type,
            balance= balance
        )
        User.insert_into_database(user1)
        userID = User.getUserID(user_name)
        accountNum = User.getAccountNumber(userID)
        User.addTransaction(accountNum, balance, "Deposit")
        session['user_id'] = userID
        session['userName'] = user_name
        return redirect(url_for('account'))
    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form.get('userName')
        password = request.form.get('password')
        result = User.check_credentials(userName, password)
        check = result[0]
        userID = result[1]
        if check:
            session['user_id'] = userID
            session['userName'] = userName
            return redirect(url_for('account'))
    return render_template('auth/login.html', title="accounts", error="Invalid credentials")

@app.route('/account')
def account():
    # Check if the user is logged in (you can implement this logic)
    if 'user_id' in session:
        # Fetch user data or perform any necessary operations here
        # For example, you can retrieve user data from the database
        # user_id = session['user_id']
        # user = User.query.filter_by(customer_user_name=user_id).first()
        accounts = User.getAccounts(session['user_id'])
        # Render the account settings template with user data
        return render_template('account.html', userID=session['user_id'], accounts=accounts, userName=session['userName'])  # Pass user data to the template
    else:
        print("You are not logged in")
        # If the user is not logged in, you can redirect them to the login page
        return redirect(url_for('login'))


@app.route('/create/account', methods=['GET'])
def create_account():
    if request.method == 'GET':
        data = User.get_user_info(session['user_id'])
        User.createAccount(data)
        #accounts = User.getAccounts(session['user_id'])
        return redirect(url_for('account'))
    else:
        return render_template('account.html', error="Invalid credentials")

@app.route('/account/deposit', methods=['POST'])
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount')
        accountNumber = request.form.get('account_number')  # Retrieve account number from the form
        userID = session.get('user_id')  # Retrieve user ID from the session
        if userID:  # Ensure user ID exists in the session
            User.deposit(amount, accountNumber)  # Call the deposit function with all parameters
            User.addTransaction(accountNumber, amount, "Deposit") #
            return redirect(url_for('account'))
        else:
            return render_template('account.html', error="Invalid session")
    else:
        return render_template('account.html', error="Invalid request method")

@app.route('/account/transfer', methods=['POST'])
def transfer():
    if request.method == 'POST':
        amount = request.form.get('amount')
        recieverAccountNumber = request.form.get('account_number')  # Retrieve selected account number from the form
        fromAccount = request.form.get('selected_account')
        userID = session.get('user_id')  # Retrieve user ID from the session
        if userID:  # Ensure user ID exists in the session
            #User.deposit(amount, userID, accountNumber)  # Call the deposit function with all parameters
            balance = User.getBalance(fromAccount)
            if balance is None:
                return render_template('account.html', error="Unable to retrieve balance for the selected account")

            try:
                if float(balance) >= float(amount):
                    User.transfer(amount, recieverAccountNumber, fromAccount)
                    User.addTransaction(recieverAccountNumber, amount, "Deposit")
                    return redirect(url_for('account'))
                else:
                    return render_template('InsufficientFund.html', error="Insufficient funds")
            except ValueError:
                return render_template('account.html', error="Invalid amount")
        else:
            return render_template('account.html', error="Invalid session")
    else:
        return render_template('account.html', error="Invalid request method")


@app.route('/account/transactions', methods=['GET', 'POST'])
def account_transactions():
    if request.method == 'POST':
        # Handle the POST request to fetch transactions data
        account_num = request.form.get('account_num')
        # Fetch transactions data and render the template
        return render_transactions_template(account_num)
    elif request.method == 'GET':
        # Handle the GET request for pagination
        account_num = request.args.get('account_num')
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=10, type=int)
        # Fetch transactions data and render the template
        return render_transactions_template(account_num, page, page_size)

def render_transactions_template(account_num, page=1, page_size=10):
    # Calculate pagination variables and fetch transactions data
    offset = (page - 1) * page_size
    transactions = User.get_paginated_transactions(account_num, offset, page_size)
    total_transactions_count = User.get_total_transactions_count(account_num)
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if offset + page_size < total_transactions_count else None
    # Render the transactions template with pagination variables and transactions data
    return render_template('transactions.html', account_num=account_num, transactions=transactions,
                           page=page, page_size=page_size, prev_page=prev_page, next_page=next_page)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    data = request.json
    userEmail = data.get('userEmail')
    amount = data.get('amount')
    
    userName = User.getUserName(userEmail)
    print(userName)
    # Process the form data and return a response
    # For example, you can return the form data as JSON
    return jsonify(Name=userName, amount=amount)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')

    # Create a response object
    response = make_response(redirect(url_for('login')))

    # Set headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response
    
if __name__ == '__main__':
    #User.getAccounts('20240203223405-244917')
    app.run(debug=True)

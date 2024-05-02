import uuid
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User():
    def __init__(self, customer_user_name, customer_first_name, customer_last_name, customer_email, customer_password, account_type, balance):
        self.customer_first_name = customer_first_name
        self.customer_last_name = customer_last_name
        self.customer_email = customer_email
        self.customer_user_name = customer_user_name
        self.customer_id = self.generate_unique_customer_id()
        self.password = self.set_password(customer_password)
        self.account_number = self.generate_unique_account_number()
        self.account_type = account_type
        self.balance = balance

    def set_password(self, password):
        # Hash the password using a secure hash algorithm
        return generate_password_hash(password)
    
    def check_password_hash(self, stored_hash, password):
        # Check if the provided password matches the stored hash
        return check_password_hash(stored_hash, password)
    
    @staticmethod
    def generate_unique_customer_id():
        # Generate a unique customer ID based on timestamp and random UUID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4().int)[:6]  # Extract the first 6 digits of a random UUID
        customer_id = f"{timestamp}-{unique_id}"
        return customer_id 
    
    @staticmethod
    def generate_unique_transaction_id():
        # Generate a unique transaction ID based on timestamp and random UUID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4().int)[:6]  # Extract the first 6 digits of a random UUID
        transaction_id = f"{timestamp}-{unique_id}"
        return transaction_id
    
    @staticmethod
    def generate_unique_account_number():
        timestamp_part = datetime.now().strftime('%y%m%d%H%M%S')
        random_part = str(uuid.uuid4().int)[:3]  # Extract the first 3 digits from a UUID
        unique_account_number = timestamp_part + random_part
        return unique_account_number
    
    @staticmethod
    def connect_to_database(query=None, parameters=(), fetchone=False, fetchall=False, db_file='BankDom.db'):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            if query:
                cursor.execute(query, parameters)
                conn.commit()
                if fetchone:
                    result = cursor.fetchone()
                    conn.close()
                    return result
                elif fetchall:
                    result = cursor.fetchall()
                    conn.close()
                    return result
            else:
                return conn
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return None

    @staticmethod
    def getUserID(userName):
        query = "SELECT UserID FROM Users WHERE Username = ?"
        parameters = (userName,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True)
        if result:
            return result[0]
        else:
            return False
        
    @staticmethod
    def getUserName(email):
        query = "SELECT FirstName FROM Users WHERE Email = ?"
        parameters = (email,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True)
        if result:
            return result[0]
        else:
            return False


    @staticmethod
    def check_credentials(userName, password, db_file='BankDom.db'):
        query = "SELECT Username, password, UserID FROM Users WHERE Username = ?"
        parameters = (userName,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True, db_file=db_file)
        if result:
            stored_password_hash = result[1]
            check = check_password_hash(stored_password_hash, password)
            if check:
                return [check, result[2]]
        return False

    @staticmethod
    def getAccountNumber(customer_id):
        query = "SELECT AccountNumber FROM Users WHERE UserID = ?"
        parameters = (customer_id,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True)
        if result:
            return result[0]
        else:
            return False

    @staticmethod
    def addTransaction(accountNumber, amount, type):
        query = "INSERT INTO Transactions (TransactionID, AccountNumber, Amount, TransactionType) VALUES (?,?,?,?)"
        transactionID = User.generate_unique_transaction_id()
        parameters = (transactionID, accountNumber, amount, type)
        return User.connect_to_database(query=query, parameters=parameters)

    @staticmethod
    def get_user_info(userID):
        query = "SELECT * FROM Users WHERE UserID = ?"
        parameters = (userID,)
        return User.connect_to_database(query=query, parameters=parameters, fetchone=True)

    @staticmethod
    def insert_into_database(data, db_file='BankDom.db'):
        query = "INSERT INTO Users (FirstName, LastName, Email, Username, UserID, Password, AccountNumber, AccountType, Balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        parameters = (data.customer_first_name, data.customer_last_name, data.customer_email, data.customer_user_name, data.customer_id, data.password, data.account_number, data.account_type, data.balance)
        return User.connect_to_database(query=query, parameters=parameters, db_file=db_file)

    @staticmethod
    def getAccounts(userID):
        query = "SELECT AccountType.Name, Users.balance, Users.AccountNumber FROM Users INNER JOIN AccountType ON Users.AccountType = AccountType.Name WHERE Users.UserID = ?"
        parameters = (userID,)
        return User.connect_to_database(query=query, parameters=parameters, fetchall=True)


    @staticmethod
    def deposit(amount, accountNumber):
        query = "UPDATE Users SET Balance = Balance + ? WHERE AccountNumber = ?"
        parameters = (amount, accountNumber)
        return User.connect_to_database(query=query, parameters=parameters)

    @staticmethod
    def transfer(amount, receiverAccountNumber, fromAccount):
        try:
            amount = float(amount)
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Balance = Balance + ? WHERE AccountNumber = ?", (amount, receiverAccountNumber))
            cursor.execute("UPDATE Users SET Balance = Balance - ? WHERE AccountNumber = ?", (amount, fromAccount))
            conn.commit()
            User.addTransaction(receiverAccountNumber, amount, "Online")
            amount = amount * (-1)
            User.addTransaction(fromAccount, amount, "Online")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def getBalance(accountNumber):
        query = "SELECT Balance FROM Users WHERE AccountNumber = ?"
        parameters = (accountNumber,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True)
        if result:
            return result[0]
        else:
            return False

    @staticmethod
    def get_paginated_transactions(account_num, offset, page_size):
        all_transactions = User.get_all_transactions(account_num)
        start_index = offset
        end_index = offset + page_size
        paginated_transactions = all_transactions[start_index:end_index]
        return paginated_transactions

    @staticmethod
    def get_all_transactions(account_num):
        query = "SELECT Amount, TransactionDate FROM Transactions WHERE AccountNumber = ? ORDER BY TransactionDate DESC"
        parameters = (account_num,)
        return User.connect_to_database(query=query, parameters=parameters, fetchall=True)

    @staticmethod
    def get_total_transactions_count(account_num):
        query = "SELECT COUNT(*) FROM Transactions WHERE AccountNumber = ?"
        parameters = (account_num,)
        result = User.connect_to_database(query=query, parameters=parameters, fetchone=True)
        if result:
            return result[0]
        else:
            return False


if __name__ == '__main__':
    user = User(
            customer_user_name='johndoe',
            customer_first_name='John',
            customer_last_name='Doe',
            customer_email='johndoe@example.com',
            customer_password='password123',
            account_type='savings',
            balance=1000.0
        )

    # Test password hashing and verification
    user.print_user_info()

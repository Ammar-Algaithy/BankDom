#importing needed libraries and models
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
    
    def getUserID(userName):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT UserID FROM Users WHERE Username = ?
            """, (userName,))
            result = cursor.fetchone()
            return result[0]
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()



    def check_credentials(userName, password, db_file='BankDom.db'):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Query the database to find a matching user by user ID
            cursor.execute("""
                SELECT Username, password, UserID FROM Users WHERE Username = ?
            """, (userName,))

            result = cursor.fetchone()
            if result:
                stored_password_hash = result[1]
                # Check if the provided password matches the stored hash
                check = check_password_hash(stored_password_hash, password)
                if check:
                    return [check, result[2]]    
            else:
                return False  # No matching user found

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()

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
    
    def getAccountNumber(customer_id):
        customer_id = customer_id
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AccountNumber FROM Users WHERE UserID = ?
            """, (customer_id,))
            result = cursor.fetchone()
            return result[0]
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()

    def addTransaction(accountNumber, amount, type):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            transactionID = User.generate_unique_transaction_id()
            cursor.execute("""
                           INSERT INTO Transactions (TransactionID, AccountNumber, Amount, TransactionType) 
                           VALUES (?,?,?,?)
                           """, (transactionID, accountNumber, amount, type))
            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()

    def get_user_info(userID):
        # Print all user information
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()

            # Query the database to find a matching user by user ID
            cursor.execute("""
                SELECT * FROM Users WHERE UserID = ?
            """, (userID,))

            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()

    def insert_into_database(self, db_file='BankDom.db'):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Insert the user data into the "Users" table
            cursor.execute("""
                INSERT INTO Users (FirstName, LastName, Email, Username, UserID, Password, AccountNumber, AccountType, Balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.customer_first_name, self.customer_last_name, self.customer_email, self.customer_user_name, self.customer_id, self.password, self.account_number, self.account_type, self.balance))

            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()
    
    def getAccounts(userID):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AccountType.Name, Users.balance, Users.AccountNumber
                FROM Users
                INNER JOIN AccountType ON Users.AccountType = AccountType.Name
                WHERE Users.UserID = ?
            """, (userID,))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False

    def createAccount(data, accountType='Saving'):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            newAccountNumber = User.generate_unique_account_number()
            
            # Insert the user data into the "Users" table
            cursor.execute("""
                INSERT INTO Users (FirstName, LastName, Email, Username, UserID, Password, AccountNumber, AccountType, Balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data[0], data[1], data[2], data[3], data[4], data[5], newAccountNumber, accountType, float(0.00)))

            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()

    def deposit(amount, userID, accountNumber):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE Users
            SET Balance = Balance + ?
            WHERE AccountNumber = ?
            """, (amount, accountNumber))
            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()

    def transfer(amount, recieverAccountNumber, fromAccount):
        try:
            amount = float(amount)
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE Users
            SET Balance = Balance + ?
            WHERE AccountNumber = ?
            """, (amount, recieverAccountNumber))
            cursor.execute("""
            UPDATE Users
            SET Balance = Balance - ?
            WHERE AccountNumber = ?
            """, (amount, fromAccount))
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()
    
    def getBalance(accountNumber):
        try:
            conn = sqlite3.connect("BankDom.db")
            cursor = conn.cursor()

            # Query the database to find a matching user by user ID
            cursor.execute("""
                SELECT Balance FROM Users WHERE AccountNumber = ?
            """, (accountNumber,))

            result = cursor.fetchone()
            return result[0]
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        finally:
            conn.close()








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

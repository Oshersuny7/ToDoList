import bcrypt

def hashPassword(password):
    salt = bcrypt.gensalt(10)
    hashPassword = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashPassword.decode('utf-8')

def comparePasswords(inputPassword, hashPassword):
    return bcrypt.checkpw(inputPassword.encode('utf-8'), hashPassword.encode('utf-8'))

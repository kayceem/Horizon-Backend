from passlib.context import CryptContext

passwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash(passwd:str):
    return passwd_context.hash(passwd)

def verify(passwd, hashed_passwd):
    return passwd_context.verify(passwd,hashed_passwd)
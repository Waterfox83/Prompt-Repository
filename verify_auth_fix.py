import jwt
import datetime

SECRET_KEY = "test_secret"
ALGORITHM = "HS256"

def test_jwt():
    print("Testing PyJWT...")
    try:
        # Encode
        payload = {"sub": "test@example.com", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"Encoded token: {token}")
        
        # Decode
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {decoded}")
        
        print("PyJWT is working correctly!")
    except AttributeError as e:
        print(f"FAILED: AttributeError - {e}")
        print("This likely means the wrong 'jwt' package is installed.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_jwt()

import hashlib
import string
import random
import os
from dotenv import load_dotenv
from typing import Optional
import validators

load_dotenv()

class ShortenerService:
    MAX_LENGTH: int = int(os.getenv("MAX_CODE_LENGTH", 10))
    ALPHABET: str = string.digits + string.ascii_letters

    def __init__(self, salt: Optional[str] = None):
        self.salt = salt if salt is not None else ""

    def base62Encode(self, num: int) -> str:
        if num == 0:
            return self.ALPHABET[0]
        
        result = ''
        base = len(self.ALPHABET)
        
        while num:
            num, rem = divmod(num, base)
            result += self.ALPHABET[rem]
            
        return result[::-1]

    def generateShortUrl(self, url: str) -> str:
        hashValue = hashlib.sha256((url + self.salt).encode()).digest()
        
        val = int.from_bytes(hashValue[:12], 'big')
        
        code = self.base62Encode(val)[:self.MAX_LENGTH]
        return code

    def randomSuffix(self, n: int = 4) -> str:
        return ''.join(random.choice(self.ALPHABET) for _ in range(n))
    
    def validateUrl(self, url: str) -> bool:
        return validators.url(url) is True
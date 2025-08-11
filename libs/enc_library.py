import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class EncLibrary:
    def __init__(self):
        pass

    def base64_enc(self, value, encoding='utf-8'):
        """Base64 encode a string"""
        if value is None:
            return ''

        byte_data = value.encode(encoding)
        return base64.b64encode(byte_data).decode('ascii')

    def base64_dec(self, value, encoding='utf-8'):
        """Base64 decode a string"""
        if value is None:
            return ''

        byte_data = base64.b64decode(value)
        return byte_data.decode(encoding)


    def two_way_enc_aes(self, key, value):
        """Two-way encryption using AES"""
        # Prepare key - truncate or pad to 16 bytes
        key_bytes = key.encode('utf-8')
        if len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        else:
            key_bytes = key_bytes.ljust(16, b'\0')

        # Create cipher with CBC mode
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)

        # Pad plaintext and encrypt
        plaintext = value.encode('utf-8')
        padded_plaintext = pad(plaintext, AES.block_size, style='pkcs7')
        ciphertext = cipher.encrypt(padded_plaintext)

        return base64.b64encode(ciphertext).decode('ascii')

    def two_way_dec_aes(self, key, value):
        """Two-way decryption using AES"""
        try:
            # Prepare key - truncate or pad to 16 bytes
            key_bytes = key.encode('utf-8')
            if len(key_bytes) > 16:
                key_bytes = key_bytes[:16]
            else:
                key_bytes = key_bytes.ljust(16, b'\0')

            # Create cipher with CBC mode
            cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)

            # Decode base64 and decrypt
            ciphertext = base64.b64decode(value)
            padded_plaintext = cipher.decrypt(ciphertext)
            plaintext = unpad(padded_plaintext, AES.block_size, style='pkcs7')

            return plaintext.decode('utf-8')
        except Exception:
            return ''



# Example usage:
if __name__ == "__main__":
    enc = EncLibrary()

    # Test base64 encoding/decoding
    test_string = """
    {"mode": "SINGLE_BOARD", "config": {"code_length": 4, "secret_code": "7828", "num_of_colors": 10, "num_of_guesses": 10}, "guesses": [{"cows": 1, "bulls": 0, "guess": "8111", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248873+00:00"}, {"cows": 1, "bulls": 0, "guess": "1234", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248879+00:00"}, {"cows": 1, "bulls": 0, "guess": "1244", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248881+00:00"}, {"cows": 1, "bulls": 0, "guess": "1299", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248882+00:00"}, {"cows": 1, "bulls": 0, "guess": "1234", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248884+00:00"}, {"cows": 0, "bulls": 0, "guess": "4444", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248885+00:00"}, {"cows": 0, "bulls": 0, "guess": "5555", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248887+00:00"}, {"cows": 0, "bulls": 0, "guess": "6666", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248889+00:00"}, {"cows": 0, "bulls": 1, "guess": "7777", "player": "Anonymous", "timestamp": "2025-08-09T13:55:10.248891+00:00"}], "players": [], "winners": [], "game_won": false, "game_over": false, "current_row": 9, "secret_code": null, "game_started": true, "remaining_guesses": 1}
    """
    
    
    encoded = enc.base64_enc(test_string)
    decoded = enc.base64_dec(encoded)
    print(f"Base64 - Original: {test_string}")
    print(f"Base64 - Encoded: {encoded}")
    print(f"Base64 - Decoded: {decoded}")
    print()

    # Test AES encryption/decryption
    key = "mySecretKey123"
    aes_encrypted = enc.two_way_enc_aes(key, test_string)
    aes_decrypted = enc.two_way_dec_aes(key, aes_encrypted)
    print(f"AES - Original: {test_string}")
    print(f"AES - Encrypted: {aes_encrypted}")
    print(f"AES - Decrypted: {aes_decrypted}")
    print()
    
    
    
    aes_base64_encoded = enc.base64_enc(aes_encrypted)
    print(f"AES Base64 - Encrypted: {aes_base64_encoded}")
    aes_base64_decrypted = enc.base64_dec(aes_base64_encoded)
    print(f"AES Base64 - Decrypted: {aes_base64_decrypted}")
    print()
    


    
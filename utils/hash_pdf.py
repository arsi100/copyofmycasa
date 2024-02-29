import hashlib
'''
-----------------------------------------------------------
Compute the sha256 hash of passed text 
-----------------------------------------------------------
Parameters:
    text: str
Returns:
    text_hash: str
-----------------------------------------------------------
'''
def hash_pdf(text : str) -> str:
    # Create a hash object
    sha256 = hashlib.sha256()
    # Update the hash with the text encoded as bytes
    sha256.update(text.encode('utf-8'))
    # Get the hexadecimal representation of the hash
    text_hash = sha256.hexdigest()

    return text_hash
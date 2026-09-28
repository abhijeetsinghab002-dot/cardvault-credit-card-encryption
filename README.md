# CardVault — Credit Card Encryption & Tokenization Demo

An educational local Flask application demonstrating AES-256-GCM authenticated encryption, random nonces, Luhn validation, PAN masking, tokenization, encrypted storage, and rate limiting.

> Use only public test card numbers such as `4242 4242 4242 4242`. Never enter real payment-card data. This demonstration is not a PCI DSS compliant payment system.

## Windows setup

Open this extracted folder in File Explorer, click the address bar, type `cmd`, and press Enter. Then run each command:

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest -v
python app.py
```

Open `http://127.0.0.1:5000`.

## How it protects the PAN

- The raw PAN exists only briefly in memory during a request.
- Luhn validation rejects malformed numbers.
- AES-256-GCM provides confidentiality and tamper detection.
- A fresh 96-bit random nonce is generated for every encryption.
- The token is authenticated as associated data.
- SQLite stores only token, masked PAN, and ciphertext.
- The AES key and database are created in `instance/`, which `.gitignore` excludes.
- API responses list only masked PANs unless the local user explicitly requests the educational decrypt operation.

## GitHub

Upload the source files and folders, but never upload `.venv/` or `instance/`.

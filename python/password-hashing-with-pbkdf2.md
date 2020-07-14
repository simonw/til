# Password hashing in Python with pbkdf2

I was researching password hashing for [datasette-auth-passwords](https://github.com/simonw/datasette-auth-passwords). I wanted very secure defaults that would work using the Python standard library without any extra dependencies.

I ended up following [Django's example](https://github.com/django/django/blob/136ec9b62bd0b105f281218d7cad54b7db7a4bab/django/contrib/auth/hashers.py#L247) and implementing `pbkdf2_sha256` with 260,000 iterations. Here's my version of the way Django does this - I chose to use the same hashed password format (`algorithm$iterations$salt$hash`) in case I wanted to change the hashing algorithm used in the future.

```python
import base64
import hashlib
import secrets

ALGORITHM = "pbkdf2_sha256"


def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)
```
Code here: https://github.com/simonw/datasette-auth-passwords/blob/ac538faf510d8ea7cf8064b9567d09c6a69e079a/datasette_auth_passwords/utils.py

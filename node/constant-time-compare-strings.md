# Constant-time comparison of strings in Node

When comparing secrets, passwords etc it's important to use a constant-time compare function to avoid timing attacks.

In Python I use `secrets.compare_digest(a, b)`, [documented here](https://docs.python.org/3/library/secrets.html#secrets.compare_digest).

I needed an equivalent in Node.js today. It has a [crypto.timingSafeEqual() function](https://nodejs.org/api/crypto.html#crypto_crypto_timingsafeequal_a_b) but it's a little tricky to use: it requires arguments that are `Buffer`, `TypedArray` or `DataView` and it throws an exception if they are not the same length.

I figured out this wrapper function so I can operate against strings of varying length:

```javascript
const { timingSafeEqual } = require('crypto');

const compare = (a, b) => {
    try {
        return timingSafeEqual(Buffer.from(a || , "utf8"), Buffer.from(b, "utf8"));
    } catch {
        return false;
    }
};
```

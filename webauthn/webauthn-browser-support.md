# WebAuthn browser support

I [started exploring](https://twitter.com/simonw/status/1476249939516616704) **[WebAuthn](https://webauthn.guide/)** today - a set of browser standards that adds support for both Yubikey 2FA hardware devices and "platform" authentication using things like Touch ID and Face ID.

## Trying it out

I have an iPhone with Face ID and a MacBook Pro (16", 2019) running macOS Catalina. I could get it to work on my iPhone but not on my Mac - at least not without a separate Yubikey (I have one lost in a bag somewhere, I should dig that out and try it).

The easiest way to try it out is using the demo on https://webauthn.io/

## Browser support

https://caniuse.com/?search=webauthn has a support matrix.

https://webauthn.me/browser-support has more browser support information, including code that detects the level of support for your current browser.

## Other places that support it

- PyPI let you use it for 2FA at https://pypi.org/manage/account/webauthn-provision - [source code here](https://github.com/pypa/warehouse/blob/eb241f9061633752672a07851cd553ad4c5cd24a/warehouse/manage/views.py#L568)
- GitHub offer it for 2FA - they call it "security keys" and the flow starts at https://github.com/settings/two_factor_authentication/configure
- Best Buy, apparently: https://www.bestbuy.com/identity/global/signin - but I think you need to configure it in an existing account before you use it to sign in.

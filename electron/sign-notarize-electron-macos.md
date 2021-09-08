# Signing and notarizing an Electron app for distribution using GitHub Actions

I had to figure this out for [Datasette Desktop](https://github.com/simonw/datasette-app).

## Pay for an Apple Developer account

First step is to pay $99/year for an [Apple Developer](https://developer.apple.com/) account.

I had a previous (expired) account with a UK address, and changing to a USA address required a support ticket - so instead I created a brand new Apple ID specifically for the developer account.

Since a later stage here involves storing the account password in a GitHub repository secret, I think this is a better way to go: I don't like the idea of my personal Apple ID account password being needed by anyone else who should be able to sign my application.

## Generate a Certificate Signing Request

First you need to generate a Certificate Signing Request using Keychain Access on a Mac - I was unable to figure out how to do this on the command-line.

Quoting https://help.apple.com/developer-account/#/devbfa00fef7:

> 1.  Launch Keychain Access located in `/Applications/Utilities`.
> 2.  Choose Keychain Access > Certificate Assistant > Request a Certificate from a Certificate Authority.
> 3.  In the Certificate Assistant dialog, enter an email address in the User Email Address field.
> 4.  In the Common Name field, enter a name for the key (for example, Gita Kumar Dev Key).
> 5.  Leave the CA Email Address field empty.
> 6.  Choose "Saved to disk", and click Continue.

This produces a `CertificateSigningRequest.certSigningRequest` file. Save that somewhere sensible.

## Creating a Developer ID Application certificate

The certificate needed is for a "Developer ID Application" - so select that option from the list of options on https://developer.apple.com/account/resources/certificates/add

Upload the `CertificateSigningRequest.certSigningRequest` file, and Apple should provide you a `developerID_application.cer` to download.

## Export it as a .p12 file

The final signing step requires a `.p12` file. It took me quite a while to figure out how to create this - in the end what worked for me was this:

1. Double-click the `developerID_application.cer` file and import it into my login keychain
2. In Keychain Access open the "My Certificates" pane
3. Select the "Developer ID Application: ..." certificate and the Private Key below it (created when generating the certificate signing request)
4. Right click and select "Export 2 items..."

![Screenshot of the Keynote export interface](https://user-images.githubusercontent.com/9599/132558174-c90410a7-8548-4642-a717-0b470788a5ea.png)

I saved the resulting file as `Developer-ID-Application-Certificates.p12`. It asked me to set a password, so I generated and saved a random one in 1Password.

## Building a signed copy of the application

At this point I turned to [electron-builder](https://www.electron.build/) to do the rest of the work. I installed it with:

    npm install electron-builder --save-dev

I added `"dist": "electron-builder --publish never"` to my `"scripts"` block in `package.json`.

Then I ran the following:

    CSC_KEY_PASSWORD=... \
      CSC_LINK=$(openssl base64 -in Developer-ID-Application-Certificates.p12) \
    npm run dist

The `CSC_KEY_PASSWORD` was the password I set earlier when I exported the certificate.

That `CSC_LINK` variable is set to the base64 encoded version of the certificate file. You can also pass the file itself, but I would need the base64 option later to work with GitHub actions.

This worked! It generated a signed `Datasette.app` package.

... which wasn't quite enough. It still wouldn't open without complaints on another machine until I had got it notarized.

## Notarizing the application

Notarizing involves uploading the application bundle to Apple's servers, where they run some automatic scans against it before returning a notarization ticket that can be "stapled" to the binary.

Thankfully [electron-notarize](https://github.com/electron/electron-notarize) does most of the work here, so I installed that:

    npm install electron-notarize --save-dev

I then went through an iteration cycle of trying out different combinations of settings until it finally worked.

I'll describe my finished configuration.

I have a file in `build/entitlements.mac.plist` containing the following:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.debugger</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-only</key>
    <true/>
    <key>com.apple.security.inherit</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
  </dict>
</plist>
```
The possible entitlements are [documented here](
https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/EntitlementKeyReference/Chapters/EnablingAppSandbox.html). I don't fully understand these ones, but they are what I got to after multiple rounds of experimentation.

I have a `scripts/notarize.js` file containing this (based on [Notarizing your Electron application](https://kilianvalkhof.com/2019/electron/notarizing-your-electron-application/) by 
Kilian Valkhof):

```javascript
/* Based on https://kilianvalkhof.com/2019/electron/notarizing-your-electron-application/ */

const { notarize } = require("electron-notarize");

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context;
  if (electronPlatformName !== "darwin") {
    return;
  }

  const appName = context.packager.appInfo.productFilename;

  return await notarize({
    appBundleId: "io.datasette.app",
    appPath: `${appOutDir}/${appName}.app`,
    appleId: process.env.APPLEID,
    appleIdPassword: process.env.APPLEIDPASS,
  });
};
```
The `"build"` section of my `package.json` looks like this:

```json
  "build": {
    "appId": "io.datasette.app",
    "mac": {
      "category": "public.app-category.developer-tools",
      "hardenedRuntime" : true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist",
      "binaries": [
        "./dist/mac/Datasette.app/Contents/Resources/python/bin/python3.9",
        "./dist/mac/Datasette.app/Contents/Resources/python/lib/python3.9/lib-dynload/xxlimited.cpython-39-darwin.so",
        "./dist/mac/Datasette.app/Contents/Resources/python/lib/python3.9/lib-dynload/_testcapi.cpython-39-darwin.so"
      ]
    },
    "afterSign": "scripts/notarize.js",
    "extraResources": [
      {
        "from": "python",
        "to": "python",
        "filter": [
          "**/*"
        ]
      }
    ]
  }
```
Again, I got here through a process of iteration - in particular, my application bundles a full copy of Python so I had to specify some additional binaries and `extraResources` - most applications will not need to do that.

Note that the `scripts/notarize.js` file uses two extra environment variables: `APPLEID` and `APPLEIDPASS`. These are the account credentials for my Apple Developer account's Apple ID.

(I also encountered an error `xcrun: error: unable to find utility "altool", not a developer tool or in PATH` - I resolved that by running `sudo xcode-select --reset`.)

## Creating an app-specific password

Another error I encountered was this one:

> Please sign in with an app-specific password. You can create one at appleid.apple.com

These can be created in the "Security" section of https://appleid.apple.com/account/home - I created one called "Notarize Apps" which I set as the `APPLEIDPASS` environment variable.

## Creating a signed and notarized build

With all of the above in place, creating a build on my laptop looked like this:
```
APPLEID=my-dedicated-appleid \
   APPLEIDPASS=app-specific-password \
   CSC_KEY_PASSWORD=key-password \
   CSC_LINK=$(openssl base64 -in Developer-ID-Application-Certificates.p12) \
   npm run dist
```
This worked! It produced a `Datasette.app` package which I could zip up, distribute to another machine, unzip and install - and it then opened without the terrifying security warning.

## Automating it all with GitHub Actions

I decided to build and notarize on _every push_ to my repository, so I could save the resulting build as an artifact and install any in-progress work on a computer to test it.

Apple [limit you to 75 notarizations a day](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow#3561440) so I think this is OK for my projects.

My full [test.yml](https://github.com/simonw/datasette-app/blob/0.1.0/.github/workflows/test.yml) looks like this:

```yaml
name: Test

on: push

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure Node caching
        uses: actions/cache@v2
        env:
          cache-name: cache-node-modules
        with:
          path: ~/.npm
          key: ${{ runner.os }}-build-${{ env.cache-name }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-build-${{ env.cache-name }}-
            ${{ runner.os }}-build-
            ${{ runner.os }}-
      - uses: actions/cache@v2
        name: Configure pip caching
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      - name: Install Node dependencies
        run: npm install
      - name: Download standalone Python
        run: |
          ./download-python.sh
      - name: Run tests
        run: npm test
        timeout-minutes: 5
      - name: Build distribution
        env:
          CSC_KEY_PASSWORD: ${{ secrets.CSC_KEY_PASSWORD }}
          CSC_LINK: ${{ secrets.CSC_LINK }}
          APPLEID: ${{ secrets.APPLEID }}
          APPLEIDPASS: ${{ secrets.APPLEIDPASS }}
        run: npm run dist
      - name: Create zip file
        run: |
          cd dist/mac
          ditto -c -k --keepParent Datasette.app Datasette.app.zip
      - name: And a README (to work around GitHub double-zips)
        run: |
          echo "More information: https://datasette.io" > dist/mac/README.txt
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: Datasette-macOS
          path: |
            dist/mac/Datasette.app.zip
            dist/mac/README.txt
```
The key stuff here is the "Build distribution" step. It sets four values that I have saved on the repository as secrets: `CSC_KEY_PASSWORD`, `CSC_LINK`, `APPLEID` and `APPLEIDPASS`.

The `CSC_LINK` variable is the base64-encoded contents of my `Developer-ID-Application-Certificates.p12` file. I generated that like so:

    openssl base64 -in developerID_application.cer

I have [a separate release.yml](https://github.com/simonw/datasette-app/blob/0.1.0/.github/workflows/release.yml) for building tagged releases, described in [this TIL](https://til.simonwillison.net/github-actions/attach-generated-file-to-release).

## The finished configuration

You can browse the code in [my 0.1.0 tag](https://github.com/simonw/datasette-app/tree/0.1.0) to see all of these parts in their final configuration, as used to create the 0.1.0 initial release of my application.

The original issue threads in which I figured this stuff out are:

- [Get an Apple developer certificate #45](https://github.com/simonw/datasette-app/issues/45)
- [Work out how to notarize the macOS application #50](https://github.com/simonw/datasette-app/issues/50)
- [GitHub Actions workflow for creating packages for releases #51](https://github.com/simonw/datasette-app/issues/51)

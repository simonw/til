# Upgrading packages with npm

There's a new version of [Vite](https://vitejs.dev/) out (3.0) and I wanted to upgrade my [datasette-table](https://github.com/simonw/datasette-table) package to use it.

I mainly followed the guide on [Update all the Node.js dependencies to their latest version](https://nodejs.dev/learn/update-all-the-nodejs-dependencies-to-their-latest-version) to work out how to do this.

My `package.json` started out containing this:

```json
  "dependencies": {
    "lit": "^2.0.0"
  },
  "devDependencies": {
    "vite": "^2.6.4"
  }
```
The `^` syntax here pins to a major version - running `npm update` will update the `package-lock.json` file to point to the highest `2.x` version of the package but won't increase the major version to `3.x`.

`npm outdated` shows if there are any releases that go beyond my pinned packages. `npm help outdated` explains [how it works in detail](https://manpages.ubuntu.com/manpages/focal/man1/npm-outdated.1.html) (`npm outdated --help` shows a less useful summary).

Running it against my project shows:
```
datasette-table % npm outdated
Package  Current  Wanted  Latest  Location           Depended by
vite      2.9.14  2.9.14   3.0.0  node_modules/vite  datasette-table
```
OK, so there's a major version upgrade available.

The `npm` tool itself doesn't have a way of applying that automatically - you need to install an extra tool, [npm-check-updates](https://manpages.ubuntu.com/manpages/focal/man1/npm-outdated.1.html):
```
npm install -g npm-check-updates
```
Then run `npm-check-updates -u` to apply those upgrades directly to `package.json`:
```
datasette-table % npm-check-updates -u
Upgrading .../datasette-table/package.json
[====================] 2/2 100%

 lit   ^2.0.0  →  ^2.2.7     
 vite  ^2.6.4  →  ^3.0.0     

Run npm install to install new versions.
```
`git diff` shows the changes it made:
```
datasette-table % git diff
diff --git a/package.json b/package.json
index 7682f38..43bfa14 100644
--- a/package.json
+++ b/package.json
@@ -13,10 +13,10 @@
     "serve": "vite preview"
   },
   "dependencies": {
-    "lit": "^2.0.0"
+    "lit": "^2.2.7"
   },
   "devDependencies": {
-    "vite": "^2.6.4"
+    "vite": "^3.0.0"
   },
   "repository": {
     "type": "git",
```
Note that it upgraded `lit` as well - `npm-check-updates` "upgrades your `package.json` dependencies to the latest versions, ignoring specified versions".

Finally, run `npm install` to install the new versions:
```
datasette-table % npm install

changed 1 package, and audited 21 packages in 901ms

4 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

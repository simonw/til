# Using Jest without a package.json

I wanted to try out [Jest](https://jestjs.io/) for writing JavaScript unit tests, in a project that wasn't set up with `package.json` and other NPM related things.

Jest looks for `*.spec.js` tests in a `__tests__` directory. It expects to find configuration in a `package.json` file but it can be passed configuration using the `-c` option - which can be a path to a JSON configuration file or can be a JSON literal.

I created a file I wanted to test in `plugins.js` which looked like this. The `module.exports` at the bottom was required so Jest could later import the code:

```javascript
var datasette = datasette || {};
datasette.plugins = (() => {
    var registry = {};
    return {
        register: (hook, fn, parameters) => {
            if (!registry[hook]) {
                registry[hook] = [];
            }
            registry[hook].push([fn, parameters]);
        },
        call: (hook, args) => {
            args = args || {};
            var results = [];
            (registry[hook] || []).forEach(([fn, parameters]) => {
                /* Call with the correct arguments */
                var result = fn.apply(fn, parameters.map(parameter => args[parameter]));
                if (result !== undefined) {
                    results.push(result);
                }
            });
            return results;
        }
    };
})();

module.exports = datasette;
```

Then I created `__tests__/plugins.spec.js` with this:

```javascript
const datasette = require("../plugins.js");

describe("Datasette Plugins", () => {
  test("it should have datasette.plugins", () => {
    expect(!!datasette.plugins).toEqual(true);
  });
  test("registering a plugin should work", () => {
    datasette.plugins.register("numbers", (a, b) => a + b, ["a", "b"]);
    var result = datasette.plugins.call("numbers", { a: 1, b: 2 });
    expect(result).toEqual([3]);
    datasette.plugins.register("numbers", (a, b) => a * b, ["a", "b"]);
    var result2 = datasette.plugins.call("numbers", { a: 1, b: 2 });
    expect(result2).toEqual([3, 2]);
  });
});
```
Now I can run Jest in the same directory as `plugins.js` like this:
```
% npx jest -c '{}'
 PASS  __tests__/plugins.spec.js
  Datasette Plugins
    ✓ it should have datasette.plugins (3 ms)
    ✓ registering a plugin should work (1 ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   0 total
Time:        1.163 s
Ran all test suites.
```

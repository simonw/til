# Very basic tsc usage

I guess I [have to learn TypeScript](https://twitter.com/simonw/status/1302517496767938561) now.

Here's how I got started in as few steps as possible, with the help of [Get Started With Typescript in 2019](https://www.robertcooper.me/get-started-with-typescript-in-2019) by Robert Cooper.

## Installation using npm

I created a new project:

    mkdir -p ~/Dropbox/Learning-TypeScript/first-typescript
    cd ~/Dropbox/Learning-TypeScript/first-typescript

Then installed the TypeScript compiler:

    npm install --save-dev typescript

Using `--global` instead of `--save-dev` would have installed in globally, but I'm not ready for that kind of commitment yet!

Next step: create a `.ts` file to start testing it out. I put the following in `greetings.ts`:

```typescript
const greeting = (person: string) => {
  console.log("Hello " + person);
};

greeting("Simon");
```

Next, compile it! Thanks to `npm install --save-dev typescript` the `tsc` compiler is now available here:

    % ./node_modules/.bin/tsc

Run without any arguments it compiles any `.ts` files in the current directory and produces matching `.js` files.

That seems to have worked:

    % node greetings.js 
    Good day Simon
    % cat greetings.js
    "use strict";
    var greeting = function (person) {
        console.log("Good day " + person);
    };
    greeting("Simon");

## Running tsc --watch

The `--watch` command continues to run and automatically compiles files when they are saved:

    % ./node_modules/.bin/tsc --watch
    [9:32:44 AM] Starting compilation in watch mode...

    [9:32:44 AM] Found 0 errors. Watching for file changes.

I changed the last line of my `greetings.ts` file to `greeting(1)` (a type error) to see what happened:

    [9:33:56 AM] File change detected. Starting incremental compilation...

    greetings.ts:5:10 - error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.

    5 greeting(1);
               ~

    [9:33:56 AM] Found 1 error. Watching for file changes.

## Running this Visual Studio Code

VSCode has built-in TypeScript support. Hit Shift+Apple+B and select the `tsc: watch` option and it runs that watch command in a embedded terminal pane inside the editor itself.

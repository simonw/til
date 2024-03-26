# Installing tools written in Go

Today I learned how to install tools from GitHub that are written in Go, using [github.com/icholy/semgrepx](https://github.com/icholy/semgrepx) as an example:

    go install github.com/icholy/semgrepx@latest

Running this command grabs a copy of the GitHub repository, compiles the Go package in there and drops the resulting binary into the `~/go/bin` folder on your computer:

```
ls -lh ~/go/bin/semgrepx
-rwxr-xr-x  1 simon  staff   2.9M Mar 25 21:08 /Users/simon/go/bin/semgrepx
```
The `@latest` reference confused me, since the repo in question didn't have a branch or tag called that.

I couldn't find the right documentation for that, but GPT-4 [confidently told me](https://chat.openai.com/share/06e62ec2-1ab3-495f-9e0c-914ef27c1e91):

> `@latest`: This specifies the version of the package you want to install. In this case, latest means that the Go tool will install the latest version of the package available. The Go tool uses the versioning information from the repository's tags to determine the latest version. If the repository follows semantic versioning, the latest version is the one with the highest version number. If there are no version tags, latest will refer to the most recent commit on the default branch of the repository.

In the absence of an official answer that looks like it might be right to me.

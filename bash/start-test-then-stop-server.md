# Start, test, then stop a localhost web server in a Bash script

I wanted to write a bash script that would start a Datasette server running, run a request against it using `curl`, then stop the server again.

It should then return an exit code indicating if the `curl` request was succesful or not.

Research notes [in this issue](https://github.com/simonw/datasette/issues/1955#issuecomment-1356630092) - here's the final script I came up with:

```bash
#!/bin/bash

# Generate certificates
python -m trustme
# This creates server.pem, server.key, client.pem

# Start the server in the background
datasette --memory \
    --ssl-keyfile=server.key \
    --ssl-certfile=server.pem \
    -p 8152 &

# Store the background process ID in a variable
server_pid=$!

# Wait for the server to start
sleep 2

# Make a test request using curl
curl -f --cacert client.pem 'https://localhost:8152/_memory.json'

# Save curl's exit code (-f option causes it to return one on HTTP errors)
curl_exit_code=$?

# Shut down the server
kill $server_pid
sleep 1

# Clean up the certificates
rm server.pem server.key client.pem

echo $curl_exit_code
exit $curl_exit_code
```
There are a few additional tricks in this - it's running `python -m trustme` to create self-signed certificates in the current directory which are used for the test - but the key parts are these:

- `datasette ... &` - starts Datasette running as a background process
- `server_pid=$!` - records the PID of the server we just started so we can shut it down later
- `curl -f ...` - makes a `curl` request, but returns an exit code that indicates if the request succeeded or was a 404 or 500 error or similar
- `curl_exit_code=$?` - records that exit code for later
- `kill $server_id` - causes the server to exit - I then did a `sleep 1` to provide time for it to output its shutdown text to the terminal
- `exit $curl_exit_code` - the exit code for the Bash script is now the same as the exit code returned by `curl`

I'm running this script [in CI in GitHub Actions](https://github.com/simonw/datasette/blob/0ea139dfe59b5c02a119c2d16ad5784b1644c42f/.github/workflows/test.yml#L39).

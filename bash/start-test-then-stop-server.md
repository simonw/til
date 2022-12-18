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

## An improved version by Jan Lehnardt

Jan Lehnardt [submitted a pull request](https://github.com/simonw/datasette/pull/1965) with this improved version:

```bash
#!/bin/bash

# Generate certificates
python -m trustme
# This creates server.pem, server.key, client.pem

cleanup () {
    rm server.pem server.key client.pem
}

# Start the server in the background
datasette --memory \
    --ssl-keyfile=server.key \
    --ssl-certfile=server.pem \
    -p 8152 &

# Store the background process ID in a variable
server_pid=$!

test_url='https://localhost:8152/_memory.json'

# Wait for the server to start

# h/t https://github.com/pouchdb/pouchdb/blob/25db22fb0ff025b8d2c698da30c6c409066baa0c/bin/run-test.sh#L102-L113
waiting=0
until $(curl --output /dev/null --silent --insecure --head --fail --max-time 2 $test_url); do
    if [ $waiting -eq 4 ]; then
        echo "$test_url can not be reached, server failed to start"
        cleanup
        exit 1
    fi
    let waiting=waiting+1
    sleep 1
done

# Make a test request using curl
curl -f --cacert client.pem $test_url

# Save curl's exit code (-f option causes it to return one on HTTP errors)
curl_exit_code=$?

# Shut down the server
kill $server_pid
waiting=0
#         show all pids
#         |       find just the $server_pid
#         |       |                  don’t match on the previous grep
#         |       |                  |            we don’t need the output
#         |       |                  |            |
until ( ! ps ax | grep $server_pid | grep -v grep > /dev/null ); do
    if [ $waiting -eq 4 ]; then
        echo "$server_pid does still exist, server failed to stop"
        cleanup
        exit 1
    fi
    let waiting=waiting+1
    sleep 1
done

# Clean up the certificates
cleanup

echo $curl_exit_code
exit $curl_exit_code
```

There's not much extra commentary I can add to this - Jan's inline comments are fantastic!

I really like the `waiting=0` pattern here for retrying up to 4 times.

Worth breaking down the `curl` command here a bit:

    curl --output /dev/null --silent --insecure --head --fail --max-time 2 $test_url

It's avoiding any output at all with a combination of writing output to `/dev/null` and using `--silent` to turn off logging.

It uses `--insecure` because our server is running with a self-signed certificate, which will produce errors without this option - and here we just want to poll until the server is up and running.

`--max-time` ensures each poll waits a maximum of two seconds.

And as before, `--fail` causes `curl` to return an exit code that indicates if the request was successful or not.

Jan used this as the impetus to start [a new library of shell utility functions](https://code.jan.io/jan/jans_shell_utils).

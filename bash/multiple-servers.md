# Running multiple servers in a single Bash script

I spotted [this script](https://github.com/varunshenoy/opendream/blob/main/run_opendream.sh) that starts the [opendream](https://github.com/varunshenoy/opendream) appication running both a Python `uvicorn` server and a `npm run start` script and it intrigued me - was it this easy to have a single Bash script run two servers? They were both started in the background with `&`, like this:

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 
uvicorn opendream.server:app --reload &
cd webapp/opendream-ui && npm install && npm run start &
wait
```
But... this didn't quite work. Hitting `Ctrl+C` quit the script, but it left the two servers running in the background. I'd like the servers to stop when the wrapping Bash script is terminated.

Is there a way to do that? I [asked GPT-4](https://chat.openai.com/share/9ccd0059-f41d-4bd9-b386-46b81bb42917) and it showed me this:

```bash
#!/bin/bash

# Function to be executed upon receiving SIGINT
cleanup() {
    echo "Caught SIGINT. Cleaning up..."
    kill $server_pid1 $server_pid2  # Terminates both server processes
    exit
}

# Set up the trap
trap cleanup SIGINT

# Start the Uvicorn server in the background
uvicorn opendream.server:app --reload &
server_pid1=$!  # Get the process ID of the last backgrounded command

# Start the npm server in the background
cd webapp/opendream-ui && npm install && npm run start &
server_pid2=$!  # Get the process ID of the last backgrounded command

# Wait indefinitely. The cleanup function will handle interruption and cleanup.
wait
```
And sure enough, that works perfectly!

There are a couple of tricks here, explained by ChatGPT's comments. Each server is started using `&` and then has its PID assigned to a variable using `$!` to access the PID.

A `cleanup()` Bash function is defined which runs `kill` against both of those stored PIDs.

Then the `trap` mechanism is used to cause that `cleanup()` function to be triggered on `SIGINT`, which is the signal that is fired when you hit `Ctrl+C`:
```bash
trap cleanup SIGINT
```
So now I have a pattern for any time I want to write a Bash script that starts multiple background processe and terminates them when the script itself exits.



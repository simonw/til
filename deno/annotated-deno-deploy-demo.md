# Annotated code for a demo of WebSocket chat in Deno Deploy

Deno Deploy is a hosted Deno service that promises [a multi-tenant JavaScript engine running in 25 data centers across the world](https://deno.com/blog/deploy-beta1/).

Today [this demo](https://dash.deno.com/playground/mini-ws-chat) by [Ondřej Žára](https://twitter.com/0ndras/status/1457027832404713479) showed up [on Hacker News](https://news.ycombinator.com/item?id=29131751), which implements "a multi-datacenter chat, client+server in 23 lines of TS".

Here's my annotated copy of the code, which I wrote while figuring out how it works.

```typescript
// listenAndServe is the Deno standard mechanism for creating an HTTP server
// https://deno.land/manual/examples/http_server#using-the-codestdhttpcode-library
import { listenAndServe } from "https://deno.land/std/http/server.ts"

// Set of all of the currently open WebSocket connections from browsers
const sockets = new Set<WebSocket>(),
/*
BroadcastChannel is a concept that is unique to the Deno Deploy environment.

https://deno.com/deploy/docs/runtime-broadcast-channel/

It is modelled after the browser API of the same name.

It sets up a channel between ALL instances of the server-side script running
in every one of the Deno Deploy global network of data centers.
*/
    channel = new BroadcastChannel(""),
    headers = {"Content-type": "text/html"},
/*
This is the bare-bones HTML for the browser side of the application

It creates a WebSocket connection back to the host, and sets it up so any
message that arrives via that WebSite will be appended to the textContent
of the pre element on the page.

The input element has an onkeyup that checks for the Enter key and sends
the value of that element over the WebSocket channel to the server.
*/
    html = `<script>let ws = new WebSocket("wss://"+location.host)
ws.onmessage = e => pre.textContent += e.data+"\\n"</script>
<input onkeyup="event.key=='Enter'&&ws.send(this.value)"><pre id=pre>`

/*
This bit does the broadcast work: any time a message is recieved from the
BroadcastChannel it is forwarded on to every single one of the currently
attached WebSocket connections, using the data in that "sockets" set.

Additionally, this covers the case of messages coming from a client connected
to THIS instance - these are also sent to the channel (see code below), but
here it spots that the message event's e.target is NOT the current instance
and sends the message to that channel so it broadcast to the other data centers.
*/
channel.onmessage = e => {
    (e.target != channel) && channel.postMessage(e.data)
    sockets.forEach(s => s.send(e.data))
}

await listenAndServe(":8080", (r: Request) => {
    try {
        /*
        Deno.upgradeWebSocket is a relatively new feature, added in Deno v1.21
        in July 2021:
        https://deno.com/blog/v1.12#server-side-websocket-support-in-native-http
        
        It gives you back a response that you should return to the client in order
        to finish establishing the WebSocket connection, and a socket object which
        you can then use for further WebSocket communication.
        */
        const { socket, response } = Deno.upgradeWebSocket(r)
        // Add it to the set so we can send to all of them later
        sockets.add(socket)
        /*
        This is a sneaky hack: when a message arrives from the WebSocket we pass it
        directly to the BroadcastChannel - then use the e.target != channel check
        above to broadcast it on to every other global instance.
        */
        socket.onmessage = channel.onmessage
        // When browser disconnects, remove the socket from the set of sockets
        socket.onclose = _ => sockets.delete(socket)
        return response
    } catch {
    /*
    I added code here to catch(e) and display e.toString() which showed me
    that the exception caught here is:

      exception: TypeError: Invalid Header: 'upgrade' header must be 'websocket'

    This is an exception thrown by Deno.upgradeWebSocket(r) if the incoming
    request does not include the "upgrade: websocket" HTTP header, which
    is added by browsers when using new WebSocket("wss://...")
    
    So here we return the HTML and headers for the application itself.
    */
    return new Response(html, {headers})
  }
})
```

Relevant links:

- [Deno listenAndServe documentation](https://deno.land/manual/examples/http_server#using-the-codestdhttpcode-library)
- [Deno Deploy BroadcastChannel documenattion](https://deno.com/deploy/docs/runtime-broadcast-channel/)
- [MDN documentation of the related BroadcastChannel browser API](https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API)

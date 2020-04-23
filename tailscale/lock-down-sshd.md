# Restricting SSH connections to devices within a Tailscale network

I'm running an AWS Lightsail instance and I want to only be able to SSH to it from devices connected to my [Tailscale](https://tailscale.com/) network.

I installed Tailscale on the instance using their [Ubuntu installation instructions](https://tailscale.com/kb/1037/install-ubuntu-1804). I have it running on my laptop and phone as well.

I ran `ifconfig tailscale0` to find the Tailscale IP for instance:
```
$ ifconfig tailscale0
tailscale0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1420
        inet 100.122.168.55  netmask 255.192.0.0  destination 100.122.168.55
        inet6 fe80::33a:342a:2733:186a  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 2147  bytes 95030 (95.0 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 990  bytes 66448 (66.4 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
Then I ran `sudo vi /etc/ssh/sshd_config` and added that address as the only `ListenAddress`:
```
#Port 22
#AddressFamily any
#ListenAddress 0.0.0.0
#ListenAddress ::
ListenAddress 100.122.168.55
```
Then restarted SSH:
```
sudo service ssh restart
```
I can now SSH to Tailscale from my laptop, but only if I use the Tailscale IP address for the server (I thought it was broken at first because I was still SSHing to the internet public IP):
```
ssh ubuntu@100.122.168.55 -i lightsail.pem
```
Bonus: point a real DNS subdomain at the Tailscale IP and you can `ssh ubuntu@realsubdomain.example.com` instead of remembering the IP address.

Handy debugging tip: `tail -f /var/log/auth.log` shows recent sign-in attempts.

Thanks to [@apenwarr for tips](https://twitter.com/apenwarr/status/1253318250131263489).

## Alternative pattern

[This conversation](https://twitter.com/moderat10n/status/1253407976330690561) questions if the above recipe will work correctly when a server reboots. It seems it's possible that sshd might start up before the `tailscale0` network has been created, resulting in problems.

[@bradfitz instead recommends](https://twitter.com/bradfitz/status/1253420075018645505) adding the following line:

    AllowUsers *@100.64.0.0/10

This will allow SSH access only from users within the Tailscale range of IPs. It shouldn't cause any problems during server startup.

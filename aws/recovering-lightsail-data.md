# Recovering data from AWS Lightsail using EC2

I ran into problems with my AWS Lightsail instance: it exceeded the CPU burst quota for too long and was suspended, and I couldn't figure out how to un-suspend it.

I had a snapshot of the hard drive and I wanted to recover the data from it. This ended up taking far longer than I expected - I imagine there's a better way of doing this but here's how I solved it.

Short version: I migrated the snapshot to EC2, then launched an EC2 instance and mounted that snapshot as an EBS volume.

Long version (because I had to figure out a lot of steps along the way):

1. I activated the Lightsail "Export to Amazon EC2" option on the snapshot
2. I waited a while for the export to complete
3. This launched a new EC2 instance for me... but for some reason I couldn't SSH into that instance. So I terminated it.
4. I used the EC2 web console to figure out the AWS identifier for the EC2 copy of the Lightsail snapshot - something like `snap-02a530e12a34`
5. I created a brand new EC2 instance and on the "Add storage" panel I added an EBS volume for `/dev/sdb` with the snapshot identifier I found in the previous step. I started this instance with a keypair so I could SSH into it.
6. I mounted the EBS volume - see section below
7. ... I used `scp` (with the keypair) to copy off the data

## Mounting the EBS volume

I hadn't worked with EBS before so this took some figuring out. My instance was configured with `/dev/sdb` as an EBS volume. I confirmed that the data was accessible like so:

    [ec2-user@ip-172-31-26-179 dev]$ sudo file -s /dev/xvdb
    /dev/xvdb: x86 boot sector; partition 1: ID=0x83, active, starthead 32, startsector 2048, 167770079 sectors, code offset 0x63

Then I created a `/data` directory and mounted the volume:

    [ec2-user@ip-172-31-26-179 dev]$ sudo mkdir /data
    [ec2-user@ip-172-31-26-179 dev]$ sudo mount /dev/xvdb1 /data

I actually tried `sudo mount /dev/xvdb /data` first and got a `mount: /data: wrong fs type` error - [this StackOverflow answer](https://serverfault.com/questions/632905/cannot-mount-an-existing-ebs-on-aws/632906#632906) helped me solve that.

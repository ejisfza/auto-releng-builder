
#!/bin/bash
# Library dependencies
yum install -y kernel-devel
yum install -y gcc*

# Mount the disk image
cd /tmp
mkdir /tmp/isomount
mount -t iso9660 -o loop /home/centos/VBoxGuestAdditions.iso /tmp/isomount

# Install the drivers
/tmp/isomount/VBoxLinuxAdditions.run

# Cleanup
umount isomount
rm -rf isomount /home/centos/VBoxGuestAdditions.iso


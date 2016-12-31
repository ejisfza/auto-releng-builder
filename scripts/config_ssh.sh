
#!/bin/bash

# Configuration steps needed to copy SSH keys between VMs

OS=$(facter operatingsystem | tr '[:upper:]' '[:lower:]')

# Check if default OS group exists
grep -q $OS /etc/group
if [ "$?" == '0' ]
then
  # Add jenkins user to OS default group
  usermod -a -G $OS jenkins
fi

# Add default password 
echo "jenkins:jenkins" | chpasswd

# Install sshpass
yum install -y sshpass

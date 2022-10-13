"""Container Helpers

The container file is just ext4 filesystem file. Can we store them in NTFS? Yeah we could.

We also must ask user where to store the the container as opposed to limited /usr/share size.

All we need to do is iterate the biggest and the free-est partitions, create some filesystem with desired size.

We may need additional size if the user asks to install a program than actually runs the program in a container.
We may also need to configure SELinux... which a new stuff."""
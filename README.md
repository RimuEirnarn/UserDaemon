# User Daemon (userd)

User Daemon is a mode-setter for certain user and a chroot based container.

## Requirements

## Basic requirements

1. Python3.6 or later
2. All depedencies required in requirements.txt are satisfied.

### Container-related

1. At least Debian based Linux since this project uses busybox that has dpkg in it
2. At least 200GB of storage installed or atleast 40GB storage available. (in plan, you can't create any more containers if atleast all partition have 20GB storage available)
3. Able to run Python3.9 with PyPy 7.3.9

## Usage or Installation

You can download or clone this then

```sh
pip install --requirements requirements.txt
```

run the main program and then done.

## License

This project is licensed in BSD 3 "New" or "Revised"

## Want to contribute or help?

Send your pull request or add a issue!

## Notice

The 'container' feature hasn't been implemented, you can see it from container_helper.py and chroot_helper.py files.

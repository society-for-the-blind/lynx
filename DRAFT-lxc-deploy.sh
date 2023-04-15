#!/usr/bin/env bash
set -euxo pipefail

# To check the latest Ubuntu LXC containers:
lxc image list ubuntu: | ag x86_64 | ag CONTAINER | sort -t '|' -k4 | less

# To avoid having to set up a storage pool and network manually. It has a lot of questions I'm not sure of though, but the defaults worked out well so far.
# https://chat.openai.com/chat/f8d2c4e1-85d4-494b-a500-325b9547661e
# !!!
# NOTE I don't think this will be needed
# https://discuss.linuxcontainers.org/t/how-do-i-know-if-lxd-is-initialized/15473/2
# instead, all needed resources will be created and invoked implicitly.
lxd init
# !!!

install_nix () {
  curl             \
  --proto '=https' \
  --tlsv1.2        \
  -sSf            \
  -L https://install.determinate.systems/nix | \
  sh -s -- install
}

CONTAINER="ubuntu-lts-dev"
STORAGE="lynx-zfs"
NETWORK="lxdbr0"

lxc storage create "${STORAGE}" zfs
lxc network create "${NETWORK}"

# WARNING Use `--ephemeral` only for testing and dev!
lxc launch                       \
  --ephemeral                    \
  --config security.nesting=true \
  --storage "${STORAGE}"         \
  --network "${NETWORK}"         \
  ubuntu:lts "${CONTAINER}"

lxc exec "${CONTAINER}" -- adduser toraritte
lxc exec "${CONTAINER}" -- adduser toraritte sudo

lxc exec "${CONTAINER}" -- sudo --login --user toraritte

# TODO
# This  is  where  the  trouble starts:  In  order  to
# install Nix, one will have to jump in the container,
# and   do  the   interactive   install.  Then   clone
# `slate-2`, and  enter `dev_shell.nix`, which  has an
# interactive step too.
#
# The  solution would  be  to create  a custom  image,
# which is quite forward, but  then where to store it?
# What are the benefits?

# TODO How to expose services in containers?
# There is  port-forwarding, bridging(?),  and reverse
# proxy  (e.g.,  NGINX).  The  last  one  seem  to  be
# the  best option,  because Lynx  already uses  it in
# production,  and it  has  to be  used (or  something
# similar) anyway for enabling HTTPS.

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:

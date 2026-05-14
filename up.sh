#!/bin/bash
set -euo pipefail
##################################################################################################################
# Author    : Erik Dubois
# Website   : https://www.erikdubois.be
##################################################################################################################
#
#   DO NOT JUST RUN THIS. EXAMINE AND JUDGE. RUN AT YOUR OWN RISK.
#
##################################################################################################################
#tput setaf 0 = black
#tput setaf 1 = red
#tput setaf 2 = green
#tput setaf 3 = yellow
#tput setaf 4 = dark blue
#tput setaf 5 = purple
#tput setaf 6 = cyan
#tput setaf 7 = gray
#tput setaf 8 = light blue
##################################################################################################################

# Stash any unstaged changes so rebase can proceed cleanly
git stash

# Pull latest changes before doing anything
git pull --rebase

# Restore stashed changes
git stash pop

# Fetch current nanorc from Kiro ISO
mkdir -p usr/share/archlinux-tweak-tool/data/nano
cp /home/erik/KIRO/kiro-iso/archiso/airootfs/etc/nanorc \
    usr/share/archlinux-tweak-tool/data/nano/nanorc

# Below command will backup everything inside the project folder
git add --all .

# skip commit if nothing staged
git diff --cached --quiet || git commit -m "update"

# Push the local files to github

branch=$(git branch --show-current)
echo "Using $branch"
git push -u origin "$branch"

echo "################################################################"
echo "###################    Git Push Done      ######################"
echo "################################################################"

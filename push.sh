#!/usr/bin/env bash
git commit -a -m 'CI'
git push root@172.24.0.8:~/robot
ssh root@172.24.0.8 "cd ~/robot;git reset HEAD --hard"
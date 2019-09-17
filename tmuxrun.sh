#!/bin/bash

tmux -c '((python3 ./start.py) && tmux detach)'

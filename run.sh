#!/bin/sh

DYLD_LIBRARY_PATH=$(pkg-config --libs-only-L glfw3 | sed "s/^-L//g") ./main.py

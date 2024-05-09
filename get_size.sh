#!/bin/bash
identify $1 | cut -d ' ' -f3 | cut -d 'x' -f1

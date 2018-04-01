#!/bin/bash

screen -mdS logview -- tail -f $1
screen -rS logview

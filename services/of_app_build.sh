#!/usr/bin/env bash

PTH=`dirname $0`'/../of_app'

make -C $PTH
if [[ $? == 0 ]]; then
	make -C $PTH run
fi
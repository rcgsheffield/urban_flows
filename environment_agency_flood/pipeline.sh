#!/usr/bin/env bash

export CONFIG

python pipeline.py -d $DATE -od $OUTPUT_DATA -k $DISTANCE -um $UPDATE_META -om $OUTPUT_META -v $VERBOSE -ad $ASSETS_DIR

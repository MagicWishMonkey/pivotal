#!/bin/bash

# python setup.py install --record files.txt && cat files.txt | xargs rm -rf && rm -rf files.txt && rm -rf dist && rm -rf build && rm -rf pivotal.egg-info

python setup.py install && rm -rf dist && rm -rf build && rm -rf pivotal.egg-info
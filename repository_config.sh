#!/bin/bash

curl https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | sudo apt-key add - && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

echo 'deb http://packages.cloud.google.com/apt apt-transport-artifact-registry-stable main' | sudo tee -a /etc/apt/sources.list.d/artifact-registry.list
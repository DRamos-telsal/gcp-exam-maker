#!/bin/bash

certification=devops

cd /home/user/exam-topics-downloader

docker run -it \
  --name examtopics-downloader \
  ghcr.io/thatonecodes/examtopics-downloader:latest \
  -p google -s $certification \
  -save-links -o $certification.txt -type txt
docker cp examtopics-downloader:/app/$certification.txt .
docker cp examtopics-downloader:/app/saved-links.txt .
docker rm examtopics-downloader

cp $certification.txt /home/user/gcp-exam-maker/exams
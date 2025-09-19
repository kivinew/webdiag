#!/bin/bash
#  Создание и запуск контейнера из образа
sudo docker run -d -p 3000:3000 --name webdiag_cont webdiag_img:latest

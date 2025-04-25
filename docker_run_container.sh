#!/bin/bash
#  Создание и запуск контейнера из образа
docker run -d -p 5000:5000 --name webdiag_cont webdiag_img:1.0

#!/bin/bash
#  Создание и запуск контейнера из образа
docker run -d -p 3000:3000 --name webdiag_cont webdiag_img:1.0

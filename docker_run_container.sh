#!/bin/bash
#  Создание и запуск контейнера из образа
docker run -d -p 6000:6000 --name webdiag_cont webdiag_img:1.0

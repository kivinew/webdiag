#!/bin/bash

#  Сборка образа
docker build -t webdiag_img:1.0 .

#  Присвоение тега (у меня версия)
docker tag webdiag_img:1.0 kivinew/webdiag_repo:1.0

#  Пуш образа на docker hub (раскомментировать)
docker push kivinew/webdiag_repo:1.0

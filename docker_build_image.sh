#!/bin/bash

#  Сборка образа
sudo docker build -t webdiag_img .

#  Присвоение тега (у меня версия)
sudo docker tag webdiag_img kivinew/webdiag_repo:1.0

#  Пуш образа на docker hub (раскомментировать)
sudo docker push kivinew/webdiag_repo:1.0

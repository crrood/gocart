# start an interactive terminal with a running mongo docker instance
docker exec -it $(docker ps -qf "name=gocart_mongodb_1") mongosh --username AzureDiamond --password hunter2
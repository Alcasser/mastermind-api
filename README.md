# Mastermind API

## Requirements

* Install the Docker tools on [Mac](https://docs.docker.com/docker-for-mac/) or [Windows](https://docs.docker.com/docker-for-windows/).


## Setup instructions

*  `git clone && cd` the repository.

In order to develop using the local environment:

*  `docker-compose -f docker-compose.yml -f envs/docker-compose.local.yml build` will build the images.
*  `docker-compose -f docker-compose.yml -f envs/docker-compose.local.yml up -d` will create the containers.
* You can restart the containers with `docker-compose restart`.
* You can stop and delete the containers, volumes, etc.. with `docker-compose down`.
* `docker ps` to see the running containers.
* `docker exec -it django-mastermind-api ./manage.py createsuperuser"` to create a new admin.
* Go to http://localhost:8000/api/admin and login with the admin user.
* Add some fields to the Game model and then run `docker exec -it django-mastermind-api ./manage.py makemigrations`, `docker exec -it django-mastermind-api ./manage.py showmigrations`, `docker exec -it django-mastermind-api ./manage.py migrate`.
* Due to the `./mastermind:/data/mastermind` volume config, you have the migrations in your working directory and you can push them to the repo.
* Notice you created the migration `0028-add-field-x` in  games > migrations folder. Want to roll back? Run `docker exec -it django-mastermind-api ./manage.py migrate 0027-migration-w`
* Use the `docker exec -it django-mastermind-api ./manage.py shell_plus` to make Django model queries
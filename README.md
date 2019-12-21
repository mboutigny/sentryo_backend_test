# Sentryo Backend Test

## Requirements
Make sure that docker is installed on your computer.
If not, you can run the following command to install it :

``sudo apt install docker.io``

## Start the project
Simply execute the launch.sh file using the following command :

``sudo ./launch.sh``

This script will build and start the docker image. 
The docker image will install all the dependencies needed to run the project.

If you need to restart the docker image, run the following commands :

``sudo docker ps``

``sudo docker kill <docker_id>``

``sudo docker system prune -a``

## Use the API
At this point you can start testing the API. You will need to be 
able to execute http requests using curl or postman for example.

Here are examples of addresses and json data you can use to make some request.

- Get all characters : http://localhost:5000/characters

- Get a specific character : http://localhost:5000/characters/<character_id>

- Add a new character : http://localhost:5000/characters
```
{
    "gender": "male",
    "name": "New User",
    "vehicles_id": [8],
    "starships_id": [39, 40]
}
```

- Update a character : http://localhost:5000/characters/<character_id>
```
{
    "eye_color": "blue",
    "homeworld": "Earth",
    "starships_id": [39]
}
```

- Delete a character : Update a character : http://localhost:5000/characters/<character_id>

*Note 1:* You will need to give valid characters IDs, vehicles IDs and starship IDs, otherwise you will get an error.

*Note 2:* If any field given in the json does not exist in the database, it will be simply ignored when adding or updating a user.
# Vibely
Daily aggregate music plays

---

###  Built with
python 3.9 and the Flask framework and uses mongodb

---
### Prerequisites
Docker installation and a running daemon


## Installation with Docker.
- This will require Docker to be already Installed. And its a shorter process compared to the second option.

Clone the repository
<pre>
git clone https://github.com/peterwade153/Vibely.git
</pre>

- Start the Docker deamon on the machine if its not running already. 

- Change directory to the folder where the project is cloned and run the command below.

<pre>
docker-compose up
</pre>

Docker will spin up containers and after the API endpoints can be accessed. Via http://localhost:8080/

The use a tool like postman to access the endpoints below.
### Endpoints

Request |       Endpoints                 |       Functionality
--------|---------------------------------|--------------------------------
POST    |  /upload                        |        Upload music file csv format (select binary for body in postman, click select file to upload file and send)
POST    |  /download/task-id              |        Downloads daily aggregated data in csv format

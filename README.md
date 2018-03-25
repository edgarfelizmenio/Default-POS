# Default-POS
Default Point of Service Application for Testing

## Runing with docker-compose
1. Execute ```docker-compose``` command.
    ```
    docker-compose up --build -d
    ```
    A container named ````defaultpos_default-pos_1``` will run in background and will automatically attach to a persistent volume.
2. Copy files/folders to the input folder.
    ```
    docker cp <files> defaultpos_default-pos_1:/code/input/
    ```
3. Execute commands
    ```
    docker exec defaultpos_default-pos_1 <command>
    ```
4. All files saved in /code/data will stay in /home/faculty/default

## Running with Docker
1. Build using Docker Compose:
    ```
    docker-compose build
    ```
2. Run the image ```default-pos:latest``` for the first time using Docker (attach volume first!)
    ```
    docker run -td --name <container_name>  default-pos:latest
    ```
    The container will run until manually terminated.
3. Copy input files to the input folder
    ```
    docker cp <filename> <container_name>:/code/input
    ```
4. Execute commands in the container.
    ```
    docker exec <container_name> <command>
    ```
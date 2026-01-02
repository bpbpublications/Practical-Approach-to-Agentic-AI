
# Setting Up PostgreSQL with Docker

Setting up a local PostgreSQL database using Docker is a great way to have a clean, isolated environment without installing it directly on your machine.
This guide will walk you through the steps to get a PostgreSQL database running in a Docker container on your local machine.

### Prerequisites

  * **Docker Desktop** installed and running on your system. You can download it from the [official Docker website](https://www.docker.com/products/docker-desktop/).

-----

## Step 1: Pull the PostgreSQL Docker Image

First, you need to download the official PostgreSQL image from Docker Hub. Open your terminal or command prompt and run the following command. The command below will pull the latest version, but you can specify a different version (e.g., `16.0`) if needed.

```bash
docker pull postgres
```

-----

## Step 2: Run the PostgreSQL Container

Now that you have the image, you can create and run a container from it. The command below is a common way to set up a basic PostgreSQL container.

```bash
docker run --name my-postgres-container -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```

Let's break down the command options:

  * `--name my-postgres-container`: Assigns a name to your container, making it easy to reference later. Feel free to change `my-postgres-container` to something more descriptive.
  * `-e POSTGRES_PASSWORD=mysecretpassword`: Sets the environment variable for the database's superuser password. **This is required.** You should replace `mysecretpassword` with a strong password of your choice.
  * `-p 5432:5432`: Maps the port `5432` on your local machine to the default PostgreSQL port `5432` inside the container. This allows you to connect to the database from your local applications using `localhost:5432`.
  * `-d`: Runs the container in **detached** mode, which means it will run in the background.
  * `postgres`: Specifies the name of the Docker image to use.

-----

## Step 3: Verify the Container is Running

To confirm that your container is up and running, you can use the `docker ps` command, which lists all active containers.

```bash
docker ps
```

You should see an entry for `my-postgres-container` in the output.

-----

## Step 4: Connect to the Database

You can now connect to your database from a SQL client or application using the following connection details:

  * **Host:** `localhost`
  * **Port:** `5432`
  * **Database:** `postgres` (the default database)
  * **Username:** `postgres` (the default superuser)
  * **Password:** `mysecretpassword` (or whatever you set in Step 2)

### Optional: Connect via the Docker CLI

You can also connect to the database directly from your terminal using the `psql` command-line client that's included in the Docker image.

First, access the container's shell:

```bash
docker exec -it my-postgres-container bash
```

Then, connect to the database using `psql`:

```bash
psql -U postgres
```

You will be prompted for the password you set earlier. After entering it, you will be in the `psql` shell and can run SQL queries. To exit, type `\q` and press Enter.

-----

## Additional Tips

  * **Stopping the Container:** To stop the container without removing it, run `docker stop my-postgres-container`.
  * **Starting the Container:** To start a stopped container, run `docker start my-postgres-container`.
  * **Removing the Container:** To completely remove the container (and any data it contains if you didn't use a volume), first stop it, and then run `docker rm my-postgres-container`.

-----

This setup provides a quick and easy way to have a disposable PostgreSQL database for your local development needs.

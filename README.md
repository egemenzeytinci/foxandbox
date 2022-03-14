# foxandbox

![homepage](/assets/images/homepage.jpg)

## Installation and Usage

Deploy the `smlar` plug-in using the following commands,

```zsh
$ git clone https://github.com/egemenzeytinci/smlar
$ cd smlar
$ USE_PGXS=1 make
$ USE_PGXS=1 make install
```

Then create `smlar` extension to PostgreSQL,

```zsh
$ psql
test=# CREATE EXTENSION smlar;
CREATE EXTENSION
```

Install requirements,
```zsh
$ pip3 install -r requirements.txt
```

You can create tables on PostgreSQL as follows,

```zsh
$ python3 migration.py default.ini # or custom ini file
```

Then, you need to download the IMDB datasets to the `temporary` path under the `system` section in the config file,

```zsh
$ wget https://datasets.imdbws.com/title.basics.tsv.gz -P /path/to/folder
$ wget https://datasets.imdbws.com/title.ratings.tsv.gz -P /path/to/folder
$ wget https://datasets.imdbws.com/title.episode.tsv.gz -P /path/to/folder
```

Then, please run DB seed script to insert static data,

```zsh
$ python3 seed.py ./default.ini # or custom ini file
```

You can now run the crawler to fetch the movie images,

```zsh
$ python3 crawl.py ./default.ini # or custom ini file
```

**Please keep in mind**, it takes a long time.

Then, please run the recommendation script to determine the clusters for the movies,

```zsh
$ python3 recommendation.py ./default.ini # or custom ini file
```

You need to install `Elasticsearch`, then below commands will create indexes and save documents,

```zsh
$ python3 indexing.py ./default.ini # or custom ini file
```

Finally, you can run web application as follows,

```zsh
$ python3 app.py ./default.ini # or custom ini file
```

from attrdict import AttrDict
from csv import DictReader
from db import engine
from db.model import Basic, Episode, Rating, TitleType
from sqlalchemy.exc import IntegrityError
from util.config import config
from util.log import logger
from termcolor import colored
import gzip
import os


class Seed:
    def __init__(self):
        # table list
        self._tables = [
            Basic,
            Episode,
            Rating,
        ]

        # source file names
        self._file_names = [
            'basics',
            'episode',
            'ratings',
        ]

        # title types for the ignore
        self._non_allowed_types = [
            'video',
            'videoGame',
            'tvEpisode',
            'audiobook',
            'radioSeries',
            'episode',
            'radioEpisode',
            'tvPilot',
        ]

        # non-boolean values
        self._integer_fields = [
            'runtimeMinutes',
            'seasonNumber',
            'episodeNumber',
        ]

    def _seed(self, table, file_name):
        """
        Create seed records according to given table

        :param db.Base table: table definition
        :param str file_name: source file name
        """
        path = f'{config.system.temporary}/title.{file_name}.tsv.gz'

        # get table name
        table_name = table.__tablename__

        tc = colored(table_name, 'green', attrs=['bold'])
        logger.info(tc + ' is seeding')

        # check if source file exists
        if not os.path.exists(path):
            raise Exception(f'The {file_name} does not exist.')

        # open gzip file
        file = gzip.open(path, 'rt')

        # extract header of csv file
        header = file.readline().strip('\n').split('\t')

        # read file as csv
        reader = DictReader(file, fieldnames=header, delimiter='\t')

        # get columns of the table
        columns = table.mapping()

        for row in reader:
            record = AttrDict()

            # populate table record by using table definition
            for original, column in columns.items():
                value = row[original]

                # handle missing values
                if value == '\\N':
                    value = None

                # handle boolean values
                if value in ['0', '1'] and original not in self._integer_fields:
                    value = value == '1'

                # handle list values
                if original == 'genres':
                    value = value.split(',') if value else None

                # handle integer id by title type
                if original == 'titleType':
                    # ignore some title types
                    if value in self._non_allowed_types:
                        break

                    value = TitleType.get(value)

                record[column] = value

            # pass ignored title types
            if 'title_type' not in record.keys() and file_name == 'basics':
                continue

            # prepare insert query
            query = table.__table__.insert().values(**record)

            # create seed record, pass if already exist
            try:
                engine.execute(query)
            except IntegrityError:
                continue
            except Exception as e:
                error = colored(e, 'red', attrs=['bold'])
                logger.error(error)

        # close file
        file.close()

    def populate(self):
        """
        Populate seed records on the database
        """
        for table, file_name in zip(self._tables, self._file_names):
            self._seed(table, file_name)

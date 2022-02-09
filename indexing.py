from elastic import es
from elastic.model import Basic
from elastic.service import ElasticBasicService
from util.log import logger

if __name__ == '__main__':
    indexes = [
        Basic,
    ]

    # create indexes on elastic
    for index in indexes:
        try:
            index.init(using=es)
        except BaseException as e:
            logger.exception(e)

    ebs = ElasticBasicService()

    # insert data to elastic index
    ebs.save_all()

from db.factory import BasicFactory, RatingFactory
from imdb import crawl


def main():
    bf = BasicFactory()
    rf = RatingFactory()

    offset = 0

    while True:
        ratings = rf.get_by_offset(offset=offset)

        # there is no record for the updating
        if len(ratings) == 0:
            break

        # get title ids from the rating objects
        rating_ids = [rating.title_id for rating in ratings]

        # get basic objects by title ids
        basics = bf.get_by_ids(rating_ids)

        if len(basics) == 0:
            offset += 1
            continue

        # get title ids for the crawling
        ids = [basic.title_id for basic in basics]

        # save updated objects
        updated_objects = crawl(ids)
        bf.save_all(updated_objects)

        offset += 1


if __name__ == '__main__':
    main()

from db.seed import Seed

if __name__ == '__main__':
    s = Seed()

    # create seed records on the database
    s.populate()

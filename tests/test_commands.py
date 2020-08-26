import mock


def test_clean_database(mongodb):
    with mock.patch("crawler_jus.database.db") as mock_mongo:
        from crawler_jus.ext.commands import clean_database

        clean_database()
        assert mock_mongo.process

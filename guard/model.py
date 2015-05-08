from datetime import datetime

import peewee as p

db = p.SqliteDatabase(None)


class Access(p.Model):
    class Meta:
        database = db

    id = p.PrimaryKeyField()
    token = p.CharField(null=False, index=True)
    pattern = p.CharField(null=False)
    comment = p.CharField()
    create_date = p.DateTimeField(default=datetime.now)

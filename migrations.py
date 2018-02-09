
def make_migrate():
    print("aditional list")
    from playhouse.migrate import DateTimeField, IntegerField, ForeignKeyField

    return [
        # ('Refund', 'buy', ForeignKeyField('Buy', null=True, default=1)),
        ('Buy', 'number', IntegerField(default=0)),
        ('Buy', 'date', DateTimeField(null=True)),
        ('Invoice', 'date', DateTimeField(null=True)),
    ]

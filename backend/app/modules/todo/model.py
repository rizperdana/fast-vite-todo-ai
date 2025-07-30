from tortoise import fields, models


class Todo(models.Model):
    """
    The Todo model
    """

    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    #: This is a username

    task = fields.CharField(max_length=500, null=False)
    detail = fields.TextField(null=True)
    finished_at = fields.DatetimeField(null=True, default=False)

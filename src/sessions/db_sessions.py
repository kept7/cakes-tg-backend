from ..settings.config import settings
from db_init import DB
from db_operations import DBUserRepository, DBOrderRepository, DBComponentRepository
from ..models.models import (
    TypeModel,
    ShapeModel,
    FlavourModel,
    ConfitModel,
)


db = DB(settings.DB_NAME)

db_user = DBUserRepository(db.session)
db_order = DBOrderRepository(db.session)

db_components_type = DBComponentRepository(db.session, TypeModel)
db_components_shape = DBComponentRepository(db.session, ShapeModel)
db_components_flavour = DBComponentRepository(db.session, FlavourModel)
db_components_confit = DBComponentRepository(db.session, ConfitModel)

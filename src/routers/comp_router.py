from fastapi import APIRouter, HTTPException

from src.sessions.db_sessions import (
    db_components_type,
    db_components_shape,
    db_components_flavour,
    db_components_confit,
)
from src.models.models import components, availability_status
from src.models.schemes import ComponentSchema


router = APIRouter(prefix="/component")


@router.get(
    "/{comp}",
    tags=["Компоненты"],
    summary="Получить информацию о компоненте",
)
async def get_component(comp: components, comp_name: str):
    if comp == "type":
        res = await db_components_type.get(comp_name)
    elif comp == "shape":
        res = await db_components_shape.get(comp_name)
    elif comp == "flavour":
        res = await db_components_flavour.get(comp_name)
    elif comp == "confit":
        res = await db_components_confit.get(comp_name)
    else:
        raise HTTPException(status_code=404, detail=f"Component {comp} doesn't exist")

    return res


@router.get(
    "",
    tags=["Компоненты"],
    summary="Получить информацию о компонентах",
)
async def get_components():
    res = [
        await db_components_type.get_all(),
        await db_components_shape.get_all(),
        await db_components_flavour.get_all(),
        await db_components_confit.get_all(),
    ]
    return res


@router.put(
    "/{comp}/{comp_id}",
    tags=["Компоненты"],
    summary="Изменить статус компонента",
)
async def update_component_availability(
    comp: components,
    comp_id: int,
    comp_avail: availability_status,
):
    if comp == "type":
        await db_components_type.update(comp_id, comp_avail)
    elif comp == "shape":
        await db_components_shape.update(comp_id, comp_avail)
    elif comp == "flavour":
        await db_components_flavour.update(comp_id, comp_avail)
    elif comp == "confit":
        await db_components_confit.update(comp_id, comp_avail)
    else:
        raise HTTPException(status_code=404, detail=f"Component {comp} doesn't exist")

    return {"ok": True, "msg": "Availability was changed"}


@router.delete(
    "/{comp}/{comp_id}",
    tags=["Компоненты"],
    summary="Удалить компонент",
)
async def delete_component(
    comp: components,
    comp_id: int,
):
    if comp == "type":
        await db_components_type.delete(comp_id)
    elif comp == "shape":
        await db_components_shape.delete(comp_id)
    elif comp == "flavour":
        await db_components_flavour.delete(comp_id)
    elif comp == "confit":
        await db_components_confit.delete(comp_id)
    else:
        raise HTTPException(status_code=404, detail=f"Component {comp} doesn't exist")

    return {"ok": True, "msg": "Component was deleted"}


@router.post(
    "",
    tags=["Компоненты"],
    summary="Добавить компонент",
)
async def add_component(comp: components, component: ComponentSchema):
    if comp == "type":
        await db_components_type.get_or_create(component)
    elif comp == "shape":
        await db_components_shape.get_or_create(component)
    elif comp == "flavour":
        await db_components_flavour.get_or_create(component)
    elif comp == "confit":
        await db_components_confit.get_or_create(component)
    else:
        raise HTTPException(status_code=404, detail=f"Component {comp} doesn't exist")

    return {"ok": True, "msg": "Component was added"}


@router.put(
    "/{comp}",
    tags=["Компоненты"],
    summary="Обновить описание компонента",
)
async def update_description(comp: components, comp_name: str, comp_desc: str):
    if comp == "type":
        await db_components_type.update_desc(comp_name, comp_desc)
    elif comp == "shape":
        await db_components_shape.update_desc(comp_name, comp_desc)
    elif comp == "flavour":
        await db_components_flavour.update_desc(comp_name, comp_desc)
    elif comp == "confit":
        await db_components_confit.update_desc(comp_name, comp_desc)
    else:
        raise HTTPException(status_code=404, detail=f"Component {comp} doesn't exist")

    return {"ok": True, "msg": "Description was updated"}

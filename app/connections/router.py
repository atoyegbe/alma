

from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def get_all_connections():
    pass

@router.post("/request/{connection_id}")
async def create_connection():
    pass

@router.post("/accept/{connection_id}")
async def accept_connection():
    pass

@router.post("/reject/{connection_id}")
async def reject_connection():
    pass

@router.post("/pending/{connection_id}")
async def pending_connection():
    pass

@router.delete("/{connection_id}")
async def delete_connection():
    pass


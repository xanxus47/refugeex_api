from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_pool

router = APIRouter(prefix="/evacuee", tags=["Evacuee"])


# ─────────────────────────────────────────
# GET /evacuee — list all with filters
# ─────────────────────────────────────────
@router.get("", response_model=dict)
async def get_evacuees(
    page: int = Query(1, ge=1),
    rows: int = Query(20, ge=1, le=100),
    barangay: Optional[str] = None,
    center_barangay: Optional[str] = None,
    evacuation_center_id: Optional[str] = None,
    evacuation_center_name: Optional[str] = None,
    is_checked_in: Optional[bool] = None,
    search: Optional[str] = None,
    household: Optional[str] = None,
    sex: Optional[str] = None,
    is_4p: Optional[bool] = None,
    is_4ps: Optional[bool] = None,
    is_pregnant: Optional[bool] = None,
    is_lactating: Optional[bool] = None,
    is_pwd: Optional[bool] = None,
    is_ip: Optional[bool] = None,
    is_solo_parent: Optional[bool] = None,
    is_single_headed: Optional[bool] = None,
    is_child_headed: Optional[bool] = None,
    is_outside_ec: Optional[bool] = None,
    is_lgbt: Optional[bool] = None,
    date_check_in: Optional[str] = None,
    sort_by: str = Query("check_in_time", enum=["check_in_time", "full_name", "barangay", "age"]),
    sort_asc: bool = False,
):
    pool = await get_pool()

    conditions = []
    params = []
    idx = 1

    if barangay:
        conditions.append(f"barangay = ${idx}"); params.append(barangay); idx += 1
    if center_barangay:
        conditions.append(f"center_barangay = ${idx}"); params.append(center_barangay); idx += 1
    if evacuation_center_id:
        conditions.append(f"evacuation_center_id = ${idx}"); params.append(evacuation_center_id); idx += 1
    if evacuation_center_name:
        conditions.append(f"evacuation_center_name ILIKE ${idx}"); params.append(f"%{evacuation_center_name}%"); idx += 1
    if is_checked_in is not None:
        conditions.append(f"is_checked_in = ${idx}"); params.append(is_checked_in); idx += 1
    if household:
        conditions.append(f"household = ${idx}"); params.append(household); idx += 1
    if sex:
        conditions.append(f"sex = ${idx}"); params.append(sex); idx += 1
    if search:
        conditions.append(f"(full_name ILIKE ${idx} OR profile_id ILIKE ${idx} OR barangay ILIKE ${idx})")
        params.append(f"%{search}%"); idx += 1
    if date_check_in:
        conditions.append(f"check_in_time::date = ${idx}"); params.append(date_check_in); idx += 1

    for field, val in [
        ("is_4p", is_4p), ("is_4ps", is_4ps), ("is_pregnant", is_pregnant),
        ("is_lactating", is_lactating), ("is_pwd", is_pwd), ("is_ip", is_ip),
        ("is_solo_parent", is_solo_parent), ("is_single_headed", is_single_headed),
        ("is_child_headed", is_child_headed), ("is_outside_ec", is_outside_ec),
        ("is_lgbt", is_lgbt),
    ]:
        if val is not None:
            conditions.append(f"{field} = ${idx}"); params.append(val); idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    order = f"ORDER BY {sort_by} {'ASC' if sort_asc else 'DESC'}"
    offset = (page - 1) * rows

    async with pool.acquire() as conn:
        total = await conn.fetchval(f"SELECT COUNT(*) FROM evacuee_details {where}", *params)
        rows_data = await conn.fetch(
            f"SELECT * FROM evacuee_details {where} {order} LIMIT {rows} OFFSET {offset}",
            *params,
        )

    return {
        "page": page,
        "rows": rows,
        "total": total,
        "data": [dict(r) for r in rows_data],
    }


# ─────────────────────────────────────────
# GET /evacuee/active — only checked-in evacuees
# ─────────────────────────────────────────
@router.get("/active", response_model=dict)
async def get_active_evacuees(
    page: int = Query(1, ge=1),
    rows: int = Query(20, ge=1, le=100),
    barangay: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("check_in_time", enum=["check_in_time", "full_name", "barangay", "age"]),
    sort_asc: bool = False,
):
    pool = await get_pool()

    conditions = ["is_checked_in = true"]
    params = []
    idx = 1

    if barangay:
        conditions.append(f"barangay = ${idx}"); params.append(barangay); idx += 1
    if search:
        conditions.append(f"(full_name ILIKE ${idx} OR profile_id ILIKE ${idx} OR barangay ILIKE ${idx})")
        params.append(f"%{search}%"); idx += 1

    where = f"WHERE {' AND '.join(conditions)}"
    order = f"ORDER BY {sort_by} {'ASC' if sort_asc else 'DESC'}"
    offset = (page - 1) * rows

    async with pool.acquire() as conn:
        total = await conn.fetchval(f"SELECT COUNT(*) FROM evacuee_details {where}", *params)
        rows_data = await conn.fetch(
            f"SELECT * FROM evacuee_details {where} {order} LIMIT {rows} OFFSET {offset}",
            *params,
        )

    return {
        "page": page,
        "rows": rows,
        "total": total,
        "data": [dict(r) for r in rows_data],
    }


# ─────────────────────────────────────────
# GET /evacuee/summary — stats overview
# ─────────────────────────────────────────
@router.get("/summary")
async def get_summary():
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_checked_in = await conn.fetchval("SELECT COUNT(*) FROM evacuee_details WHERE is_checked_in = true")
        total_checked_out = await conn.fetchval("SELECT COUNT(*) FROM evacuee_details WHERE is_checked_in = false")
        total_all_time = await conn.fetchval("SELECT COUNT(*) FROM evacuee_details")

        by_barangay = await conn.fetch("""
            SELECT barangay,
                   COUNT(*) FILTER (WHERE is_checked_in = true) AS checked_in,
                   COUNT(*) FILTER (WHERE is_checked_in = false) AS checked_out
            FROM evacuee_details
            GROUP BY barangay
            ORDER BY checked_in DESC
        """)

        by_center = await conn.fetch("""
            SELECT evacuation_center_id, evacuation_center_name,
                   COUNT(*) FILTER (WHERE is_checked_in = true) AS checked_in,
                   COUNT(*) FILTER (WHERE is_checked_in = false) AS checked_out
            FROM evacuee_details
            GROUP BY evacuation_center_id, evacuation_center_name
            ORDER BY checked_in DESC
        """)

        sectors = await conn.fetchrow("""
            SELECT
                COUNT(*) FILTER (WHERE is_4p = true OR is_4ps = true) AS is_4p,
                COUNT(*) FILTER (WHERE is_pregnant = true) AS is_pregnant,
                COUNT(*) FILTER (WHERE is_lactating = true) AS is_lactating,
                COUNT(*) FILTER (WHERE is_pwd = true) AS is_pwd,
                COUNT(*) FILTER (WHERE is_ip = true) AS is_ip,
                COUNT(*) FILTER (WHERE is_solo_parent = true) AS is_solo_parent,
                COUNT(*) FILTER (WHERE is_single_headed = true) AS is_single_headed,
                COUNT(*) FILTER (WHERE is_child_headed = true) AS is_child_headed,
                COUNT(*) FILTER (WHERE is_outside_ec = true) AS is_outside_ec,
                COUNT(*) FILTER (WHERE is_lgbt = true) AS is_lgbt
            FROM evacuee_details
            WHERE is_checked_in = true
        """)

    return {
        "total_checked_in": total_checked_in,
        "total_checked_out": total_checked_out,
        "total_all_time": total_all_time,
        "by_barangay": [dict(r) for r in by_barangay],
        "by_evacuation_center": [dict(r) for r in by_center],
        "vulnerable_sectors": dict(sectors),
    }


# ─────────────────────────────────────────
# GET /evacuee/barangay/{barangay_name} — filter by barangay
# ─────────────────────────────────────────
@router.get("/barangay/{barangay_name}", response_model=dict)
async def get_evacuees_by_barangay(
    barangay_name: str,
    page: int = Query(1, ge=1),
    rows: int = Query(20, ge=1, le=100),
    is_checked_in: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("check_in_time", enum=["check_in_time", "full_name", "age"]),
    sort_asc: bool = False,
):
    pool = await get_pool()

    conditions = ["barangay = $1"]
    params = [barangay_name]
    idx = 2

    if is_checked_in is not None:
        conditions.append(f"is_checked_in = ${idx}"); params.append(is_checked_in); idx += 1
    if search:
        conditions.append(f"(full_name ILIKE ${idx} OR profile_id ILIKE ${idx})")
        params.append(f"%{search}%"); idx += 1

    where = f"WHERE {' AND '.join(conditions)}"
    order = f"ORDER BY {sort_by} {'ASC' if sort_asc else 'DESC'}"
    offset = (page - 1) * rows

    async with pool.acquire() as conn:
        total = await conn.fetchval(f"SELECT COUNT(*) FROM evacuee_details {where}", *params)
        rows_data = await conn.fetch(
            f"SELECT * FROM evacuee_details {where} {order} LIMIT {rows} OFFSET {offset}",
            *params,
        )

    if total == 0:
        raise HTTPException(status_code=404, detail=f"No evacuees found for barangay '{barangay_name}'")

    return {
        "barangay": barangay_name,
        "page": page,
        "rows": rows,
        "total": total,
        "data": [dict(r) for r in rows_data],
    }


# ─────────────────────────────────────────
# GET /evacuee/{id} — single record
# ─────────────────────────────────────────
@router.get("/{id}")
async def get_evacuee_by_id(id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM evacuee_details WHERE id = $1", id)
    if not row:
        raise HTTPException(status_code=404, detail="Evacuee not found")
    return dict(row)


# ─────────────────────────────────────────
# PATCH /evacuee/{id}/checkout — check out by record id
# ─────────────────────────────────────────
@router.patch("/{id}/checkout")
async def check_out_by_id(id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, profile_id, full_name, is_checked_in FROM evacuee_details WHERE id = $1", id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Record not found")
        if not row["is_checked_in"]:
            raise HTTPException(status_code=409, detail="Evacuee is already checked out")

        updated = await conn.fetchrow("""
            UPDATE evacuee_details
            SET is_checked_in = false,
                check_out_time = NOW(),
                updated_at = NOW()
            WHERE id = $1
            RETURNING id, profile_id, full_name, check_out_time, is_checked_in
        """, id)

    return {
        "message": "Checked out successfully",
        "data": dict(updated),
    }


# ─────────────────────────────────────────
# PATCH /evacuee/checkout/{profile_id} — check out by profile_id
# ─────────────────────────────────────────
@router.patch("/checkout/{profile_id}")
async def check_out_by_profile(profile_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, full_name, is_checked_in FROM evacuee_details WHERE profile_id = $1 AND is_checked_in = true",
            profile_id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="No active check-in found for this profile")

        updated = await conn.fetchrow("""
            UPDATE evacuee_details
            SET is_checked_in = false,
                check_out_time = NOW(),
                updated_at = NOW()
            WHERE profile_id = $1 AND is_checked_in = true
            RETURNING id, profile_id, full_name, check_out_time, is_checked_in
        """, profile_id)

    return {
        "message": "Checked out successfully",
        "data": dict(updated),
    }


# ─────────────────────────────────────────
# POST /evacuee/checkout-all — bulk check out all currently checked in
# ─────────────────────────────────────────
@router.post("/checkout-all")
async def check_out_all(
    evacuation_center_id: Optional[str] = Query(None, description="Filter by center, or leave blank for all"),
    barangay: Optional[str] = Query(None),
):
    pool = await get_pool()

    conditions = ["is_checked_in = true"]
    params = []
    idx = 1

    if evacuation_center_id:
        conditions.append(f"evacuation_center_id = ${idx}"); params.append(evacuation_center_id); idx += 1
    if barangay:
        conditions.append(f"barangay = ${idx}"); params.append(barangay); idx += 1

    where = f"WHERE {' AND '.join(conditions)}"

    async with pool.acquire() as conn:
        result = await conn.fetch(f"""
            UPDATE evacuee_details
            SET is_checked_in = false,
                check_out_time = NOW(),
                updated_at = NOW()
            {where}
            RETURNING id, profile_id, full_name
        """, *params)

    return {
        "message": f"Checked out {len(result)} evacuee(s)",
        "total_checked_out": len(result),
        "data": [dict(r) for r in result],
    }
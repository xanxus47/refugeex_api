from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_pool

router = APIRouter()


# ─────────────────────────────────────────
# PATCH /{id}/checkout — check out by record id
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
# PATCH /checkout/{profile_id} — check out by profile_id
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
# POST /checkout-all — bulk check out all currently checked in
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
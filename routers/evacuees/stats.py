from fastapi import APIRouter
from database import get_pool

router = APIRouter()


# ─────────────────────────────────────────
# GET /summary — stats overview
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
# GET /summary/barangay — per barangay stats
# ─────────────────────────────────────────
@router.get("/summary/barangay")
async def get_summary_by_barangay():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows_data = await conn.fetch("""
            SELECT
                barangay,
                COUNT(*) FILTER (WHERE is_checked_in = true)  AS checked_in,
                COUNT(*) FILTER (WHERE is_checked_in = false) AS checked_out,
                COUNT(*)                                        AS total_all_time,
                COUNT(*) FILTER (WHERE is_checked_in = true AND sex = 'Male')   AS male,
                COUNT(*) FILTER (WHERE is_checked_in = true AND sex = 'Female') AS female,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_pwd = true)         AS pwd,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_pregnant = true)    AS pregnant,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_lactating = true)   AS lactating,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_solo_parent = true) AS solo_parent,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_ip = true)          AS ip,
                COUNT(*) FILTER (WHERE is_checked_in = true AND is_lgbt = true)        AS lgbt,
                COUNT(*) FILTER (WHERE is_checked_in = true AND (is_4p = true OR is_4ps = true)) AS is_4p
            FROM evacuee_details
            GROUP BY barangay
            ORDER BY checked_in DESC
        """)

    return {
        "total_barangays": len(rows_data),
        "data": [dict(r) for r in rows_data],
    }
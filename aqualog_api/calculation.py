from fastapi import APIRouter, Request

from aqualog_api.responses import success_response

GRAMS_PER_LITER_PER_PPT = 1.1  # grams per liter per ppt of salinity change

def build_calculation_router() -> APIRouter:
    router = APIRouter()

    @router.get("/calculate/dose/salinity")
    async def salinity_dose(
        request: Request,
        volume: float,
        current: float,
        target: float,
    ):
        request_id = getattr(request.state, "request_id", "unknown")
        quantity = (target - current) * GRAMS_PER_LITER_PER_PPT * volume
        return success_response(
            {
                "volume": volume,
                "current": current,
                "target": target,
                "quantity": quantity,
            },
            request_id=request_id,
        )

    return router
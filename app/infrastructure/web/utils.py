def success(payload: dict, status_code: int = 200):
    return {"success": True, **payload}, status_code

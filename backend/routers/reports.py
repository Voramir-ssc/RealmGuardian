from fastapi import APIRouter, HTTPException
import backup
from discord_report import send_weekly_report

router = APIRouter(prefix="/api", tags=["System & Reports"])

@router.post('/backup')
def trigger_backup():
    """ Trigger a manual SQLite database backup. """
    success = backup.create_backup()
    if success:
        return {'status': 'success', 'message': 'Backup created'}
    else:
        raise HTTPException(status_code=500, detail='Backup failed')

@router.post('/report/trigger')
def trigger_manual_report():
    """ Triggers the Discord Weekly Report manually for testing """
    try:
        import threading
        threading.Thread(target=send_weekly_report).start()
        return {"status": "success", "message": "Manual report triggered in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

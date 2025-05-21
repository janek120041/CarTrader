from datetime import datetime

def inject_datetime():
    return {'now': datetime.utcnow()} 
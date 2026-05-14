import json
import logging
import sys
from datetime import datetime, timezone
from logging.config import dictConfig

from flask import has_request_context, request


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "time": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if has_request_context():
            log["method"] = request.method
            log["path"] = request.path
            log["ip"] = request.remote_addr

        # take any extra fields 
        for key, value in record.__dict__.items():
            # tạo log field cho mỗi extra field, tránh ghi đè các field mặc định của log record
            # tạo 1 logrecord rỗng để kiểm tra xem key có phải là field mặc định hay không
            if key not in logging.LogRecord("", "", "", "", "", (), None).__dict__:
                log[key] = value
        return json.dumps(log)


def setup_logging(app):
    # ghi ra terminal 
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    
    logger = logging.getLogger()
    # chỉ lấy từ info trở lên, bỏ qua debug
    logger.setLevel(logging.INFO)
    
    # để tránh tạo nhiều handler khi được gọi nhiều lần 
    logger.handlers.clear()
    logger.addHandler(handler)
    
    # tắt log của werkzeug để tránh bị trùng lặp với log của app
    logging.getLogger("werkzeug").disabled = True
    
def register_request_logging(app):
    logger = logging.getLogger("app")
    
    @app.before_request
    def log_request():
        if request.path == "/metrics":
            return
        logger.info("request received")
        
    @app.after_request
    def log_response(response):
        if request.path == "/metrics":
            return response
        logger.info(f"request completed status={response.status_code}")
        return response

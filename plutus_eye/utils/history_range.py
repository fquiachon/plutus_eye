from datetime import datetime, timedelta


class GlobalHistory:

    def get_range(self, days=6):
        end_datetime = datetime.now()
        start_datetime = end_datetime - timedelta(days=days)
        return start_datetime.timestamp(), end_datetime.timestamp()


class PSEHistory:

    def get_range(self, days=6):
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        start_date = now - timedelta(days=days)
        prev = start_date.strftime('%Y-%m-%d')
        return prev, today


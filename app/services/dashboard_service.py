"""
Dashboard Service

Provides dashboard statistics.
"""

from app.services import analytics_service


class DashboardService:

    def get_dashboard(self):

        return analytics_service.summary()
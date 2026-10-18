"""Optional local Azure Functions host for the existing simulated business API.

Run with Core Tools, not Uvicorn. This adapter does not provision or deploy Azure resources.
"""

import azure.functions as func

from pharmaops.business import app as business_api

app = func.AsgiFunctionApp(
    app=business_api,
    http_auth_level=func.AuthLevel.ANONYMOUS,
    function_name="pharmaops_business_api",
)

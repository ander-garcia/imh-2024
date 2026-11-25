"""Put OPCUA_DEFAULT_ENDPOINT first in opcua-client's saved address list.

opcua-client has no command-line option for the server URL; it reads the
"address_list" value from QSettings. This writes that value with the same
organization/application names the client uses, so the endpoint is preselected.
"""
import os
import sys

from PyQt6.QtCore import QCoreApplication, QSettings

endpoint = os.environ.get("OPCUA_DEFAULT_ENDPOINT")
if not endpoint:
    sys.exit(0)

app = QCoreApplication(["opcua-client"])
# Same names opcua-client sets in uaclient/mainwindow.py before creating its QSettings
QCoreApplication.setOrganizationName("FreeOpcUa")
QCoreApplication.setApplicationName("OpcUaClient")
settings = QSettings()
addresses = settings.value("address_list", []) or []
if isinstance(addresses, str):
    addresses = [addresses]
addresses = [endpoint] + [a for a in addresses if a != endpoint]
settings.setValue("address_list", addresses[:10])
settings.sync()
print(f"opcua-client default endpoint: {endpoint} ({settings.fileName()})")

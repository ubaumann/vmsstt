import logging
import requests
import time
from PIL import Image
from io import BytesIO
from pyVim import connect
from pyVmomi import vim

logger = logging.getLogger(__name__)


def wait_until_sucess(task, retry=5, factor=2.0) -> None:
    """Check if task is success or wait seconds * factor"""
    seconds = 1
    for _ in range(retry):
        if task.info.state == "success":
            return
        if task.info.state in ["error"]:
            raise Exception("Screenshot tasked failed")
        logger.debug(
            "task not successful yet. Retry in %d seconds. state: %s",
            seconds,
            task.info.state,
        )
        time.sleep(seconds)
        seconds *= factor
    logger.error("task not successful. state: %s", task.info.state)
    raise Exception("Screenshot task not seccessful")


class ScreenShot(object):
    """
    Object to create screenshot on vCenter and download the picute
    """

    def __init__(self, vm_name, host, user, password, port=443, verify=True) -> None:
        self._vcenter = None
        self._vm = None
        self._image_url = None
        self.vm_name = vm_name
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.verify = verify

    def connect(self) -> None:
        """Connect to the vCenter"""
        connection_details = {
            "host": self.host,
            "user": self.user,
            "pwd": self.password,
            "port": self.port,
        }
        if self.verify:
            self._vcenter = connect.SmartConnect(**connection_details)
            logger.debug("Secure connected to %s", self.host)
        else:
            self._vcenter = connect.SmartConnectNoSSL(**connection_details)
            logger.debug("Not secure connected to %s", self.host)

    def search(self) -> None:
        """Search for the VM object"""
        content = self._vcenter.RetrieveContent()
        self._vm = content.searchIndex.FindByDnsName(
            dnsName=self.vm_name, vmSearch=True
        )
        logger.debug("Searched for %s. Found VM %s", self.vm_name, self._vm.name)

    def _get_datacenter(self) -> str:
        """Internal fuction for searching the datacenter name"""
        parent = self._vm.parent
        while True:
            logger.debug("Looking for the datacenter. Level: %s", parent.name)
            if isinstance(parent, vim.Datacenter):
                return parent.name
            parent = parent.parent

    def _power_on(self) -> bool:
        """Check if VM is powerd on"""
        logger.debug("PowerState is %s", self._vm.summary.runtime.powerState)
        return self._vm.summary.runtime.powerState == "poweredOn"

    def get(self) -> Image.Image:
        """
        1. Create Screenshot Task
        2. Wait for task to become successful
        3. Build picture URL
        4. Download picture
        5. Return PIL Image object
        """
        if self._power_on():
            task = self._vm.CreateScreenshot()
            wait_until_sucess(task)
            location = task.info.result
            logger.debug("Location: %s", location)
            # location: '[ISCSI-VOL-01] sr-000040/sr-000040-2.png'
            datastore, path = location.split()
            logger.debug("Datastore: %s, Path: %s", datastore, path)
            self._image_url = f"https://{self.host}/folder/{path}?dsName={datastore.strip('[]')}&dcPath={self._get_datacenter()}"
            logger.debug("Image url: %s", self._image_url)
            response = requests.get(
                url=self._image_url, auth=(self.user, self.password), verify=self.verify
            )
            logger.debug("Get response: %s", response)
            return Image.open(BytesIO(response.content))
        logger.error("_power_on is not True")
        raise Exception("VM not running")

    def delete(self) -> None:
        """Delete picture file on datastore"""
        logger.debug("Deleting url: %s", self._image_url)
        response = requests.delete(
            url=self._image_url, auth=(self.user, self.password), verify=self.verify
        )
        logger.debug("Delete response: %s", response)

    def disconnect(self) -> None:
        """Close session to vCenter"""
        connect.Disconnect(self._vcenter)
        logger.debug("Disconnected from %s", self.host)

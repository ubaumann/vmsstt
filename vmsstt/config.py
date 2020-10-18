import os

VCENTER_HOST = os.environ.get('VCENTER_HOST', 'vcenter')
VCENTER_USER = os.environ.get('VCENTER_USER', 'administrator@vsphere.local')
VCENTER_PASSWORD = os.environ.get('VCENTER_PASSWORD', 'vcenter.vsphere.local')
VERIFY = not os.environ.get('VMSSTT_VERIFY', 'True').lower() in ['false', 'no', 'off']
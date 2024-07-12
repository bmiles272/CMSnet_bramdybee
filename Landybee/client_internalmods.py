"""Generated client methods for the LanDB SOAP API.

Generated from: https://network.cern.ch/sc/soap/soap.fcgi?v=6&WSDL
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import suds.client  # type: ignore[import-untyped]
import suds.xsd.doctor  # type: ignore[import-untyped]
from dotenv import load_dotenv, find_dotenv, dotenv_values
import os
import time
import os.path as path
from typing import Optional

if TYPE_CHECKING:
    from .types import *  # noqa: F403



class LanDB:
    """LanDB client interface."""

    def __init__(self: Self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """Initialize the LanDB client.

        Optionally, authenticate the client by providing a username and password.
        """
        self.client = suds.client.Client(
            url="https://network.cern.ch/sc/soap/soap.fcgi?v=6&WSDL",
            doctor=suds.xsd.doctor.ImportDoctor(
                suds.xsd.doctor.Import("http://schemas.xmlsoap.org/soap/encoding/"),
            ),
            cache=None,
        )
        self.authenticated = False
        
        def file_older_than_9half(file): 
            file_time = path.getmtime(file) 
            # Check against 24 hours 
            return ((time.time() - file_time) / 3600 > 9.5)
        
        if os.path.exists('.env') and not file_older_than_9half('.env'):
            load_dotenv(find_dotenv(filename= '.env'))
            token = os.getenv('AUTH_TOKEN')
            print(token)
            if token:
                self.client.set_options(soapheaders={"Auth": {"token": token}})
                self.authenticated = True

        elif username and password:
            token = self.getAuthToken(username, password, "CERN")
            self.client.set_options(soapheaders={"Auth": {"token": token}})
            self.authenticated = True
            if self.authenticated == True:
                #print(envfilename)
                file = open('.env', 'w')
                file.write('AUTH_TOKEN = ' + token)
            load_dotenv(find_dotenv(filename= '.env'))
            print(type(os.getenv('AUTH_TOKEN')))
                

        elif username or password:
            msg = "Either provide username and password, or neither"
            raise ValueError(msg)

    def _confirm_authenticated(self: Self) -> None:
        if not self.authenticated:
            msg = 'This method requires authentication: `LanDB("username", "password")`'
            raise PermissionError(msg)

    def getAuthToken(self: Self, Login: str, Password: str, Type: str) -> str:
        return self.client.service.getAuthToken(Login, Password, Type)

    def searchDevice(self: Self, DeviceSearch: DeviceSearch | DeviceSearchDict) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.searchDevice(DeviceSearch)

    def getDeviceBasicInfo(self: Self, DeviceName: str) -> DeviceBasicInfo:
        return self.client.service.getDeviceBasicInfo(DeviceName)

    def getDeviceInfo(self: Self, DeviceName: str) -> DeviceInfo:
        self._confirm_authenticated()
        return self.client.service.getDeviceInfo(DeviceName)

    def getDeviceInfoArray(self: Self, DeviceNameList: ArrayOfString) -> ArrayOfDeviceInfo:
        self._confirm_authenticated()
        return self.client.service.getDeviceInfoArray(DeviceNameList)

    def getDeviceInfoFromNameMAC(self: Self, DeviceName: str, MAC: str) -> DeviceInfo:
        return self.client.service.getDeviceInfoFromNameMAC(DeviceName, MAC)

    def getMyDeviceInfo(self: Self) -> DeviceInfo:
        return self.client.service.getMyDeviceInfo()

    def getLastChangedDevices(self: Self, Minutes: int) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.getLastChangedDevices(Minutes)

    def bulkInsert(self: Self, Device: DeviceInput | DeviceInputDict, Cards: ArrayOfInterfaceCards | ArrayOfInterfaceCardsDict, Interfaces: ArrayOfBulkInterfaces | ArrayOfBulkInterfacesDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.bulkInsert(Device, Cards, Interfaces)

    def bulkInsertAuto(self: Self, Device: DeviceInput | DeviceInputDict, Cards: ArrayOfInterfaceCards | ArrayOfInterfaceCardsDict, Interfaces: ArrayOfBulkInterfacesAuto | ArrayOfBulkInterfacesAutoDict) -> bool:
        return self.client.service.bulkInsertAuto(Device, Cards, Interfaces)

    def bulkRemove(self: Self, DeviceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.bulkRemove(DeviceName)

    def deviceInsert(self: Self, Device: DeviceInput | DeviceInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceInsert(Device)

    def deviceAddCard(self: Self, DeviceName: str, InterfaceCard: InterfaceCard | InterfaceCardDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceAddCard(DeviceName, InterfaceCard)

    def deviceAddBulkInterface(self: Self, DeviceName: str, BulkInterface: BulkInterface | BulkInterfaceDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceAddBulkInterface(DeviceName, BulkInterface)

    def deviceRemove(self: Self, DeviceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceRemove(DeviceName)

    def deviceRemoveCard(self: Self, DeviceName: str, HardwareAddress: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceRemoveCard(DeviceName, HardwareAddress)

    def deviceRemoveBulkInterface(self: Self, DeviceName: str, InterfaceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceRemoveBulkInterface(DeviceName, InterfaceName)

    def deviceMoveBulkInterface(self: Self, DeviceName: str, InterfaceName: str, BulkInterface: BulkInterface | BulkInterfaceDict, BulkMoveOptions: BulkMoveOptions | BulkMoveOptionsDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceMoveBulkInterface(DeviceName, InterfaceName, BulkInterface, BulkMoveOptions)

    def deviceUpdate(self: Self, DeviceName: str, DeviceInput: DeviceInput | DeviceInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceUpdate(DeviceName, DeviceInput)

    def deviceGlobalRename(self: Self, DeviceName: str, NewDeviceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceGlobalRename(DeviceName, NewDeviceName)

    def setHCPResponse(self: Self, DeviceList: ArrayOfString, HCPFlag: bool) -> bool:
        self._confirm_authenticated()
        return self.client.service.setHCPResponse(DeviceList, HCPFlag)

    def deviceUpdateIPv6Ready(self: Self, DeviceName: str, IPv6Ready: bool) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceUpdateIPv6Ready(DeviceName, IPv6Ready)

    def deviceUpdateManagerLock(self: Self, DeviceName: str, ManagerLocked: bool) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceUpdateManagerLock(DeviceName, ManagerLocked)

    def deviceSetBOOTPInfo(self: Self, Device: str, Server: str, ImagePath: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceSetBOOTPInfo(Device, Server, ImagePath)

    def deviceRemoveBOOTPInfo(self: Self, Device: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceRemoveBOOTPInfo(Device)

    def getBOOTPInfo(self: Self, Device: str) -> BOOTPInfo:
        self._confirm_authenticated()
        return self.client.service.getBOOTPInfo(Device)

    def getBulkInterfaceInfo(self: Self, InterfaceName: str) -> BulkInterface:
        self._confirm_authenticated()
        return self.client.service.getBulkInterfaceInfo(InterfaceName)

    def setInsertAddress(self: Self, Set: str, Address: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setInsertAddress(Set, Address)

    def setInsertService(self: Self, Set: str, Service: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setInsertService(Set, Service)

    def setDeleteAddress(self: Self, Set: str, Address: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setDeleteAddress(Set, Address)

    def setDeleteService(self: Self, Set: str, Service: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setDeleteService(Set, Service)

    def getSetInfo(self: Self, SetName: str) -> SetInfo:
        self._confirm_authenticated()
        return self.client.service.getSetInfo(SetName)

    def getSetNameFromID(self: Self, SetID: int) -> str:
        self._confirm_authenticated()
        return self.client.service.getSetNameFromID(SetID)

    def getSetAllInterfaces(self: Self, SetName: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.getSetAllInterfaces(SetName)

    def getSetInterfacesTrusting(self: Self, SetName: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.getSetInterfacesTrusting(SetName)

    def getHCPInfoArray(self: Self, Hosts: ArrayOfString) -> ArrayOfInetInfo:
        self._confirm_authenticated()
        return self.client.service.getHCPInfoArray(Hosts)

    def getDevicesFromService(self: Self, Service: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.getDevicesFromService(Service)

    def getSwitchesFromService(self: Self, Service: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.getSwitchesFromService(Service)

    def getSwitchInfo(self: Self, SwitchName: str) -> ArrayOfSwitchPort:
        self._confirm_authenticated()
        return self.client.service.getSwitchInfo(SwitchName)

    def getConnectionsFromDevice(self: Self, DeviceName: str) -> ArrayOfConnection:
        self._confirm_authenticated()
        return self.client.service.getConnectionsFromDevice(DeviceName)

    def getOutletLocationFromSwitchPort(self: Self, SwitchName: str, PortName: str) -> OutletLocation:
        self._confirm_authenticated()
        return self.client.service.getOutletLocationFromSwitchPort(SwitchName, PortName)

    def getCurrentConnection(self: Self, ip: str, HardwareAddressList: ArrayOfString) -> ArrayOfObservedSwitchConnection:
        return self.client.service.getCurrentConnection(ip, HardwareAddressList)

    def getMyCurrentConnection(self: Self, HardwareAddressList: ArrayOfString) -> ArrayOfObservedSwitchConnection:
        return self.client.service.getMyCurrentConnection(HardwareAddressList)

    def enableFanOutFromSwitchPort(self: Self, SwitchName: str, PortName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.enableFanOutFromSwitchPort(SwitchName, PortName)

    def bindUnbindInterface(self: Self, InterfaceName: str, HardwareAddress: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.bindUnbindInterface(InterfaceName, HardwareAddress)

    def interfaceAddAlias(self: Self, InterfaceName: str, Alias: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceAddAlias(InterfaceName, Alias)

    def interfaceRemoveAlias(self: Self, InterfaceName: str, Alias: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceRemoveAlias(InterfaceName, Alias)

    def interfaceMoveAlias(self: Self, InterfaceName: str, Alias: str, NewInterfaceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceMoveAlias(InterfaceName, Alias, NewInterfaceName)

    def interfaceRename(self: Self, InterfaceName: str, NewInterfaceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceRename(InterfaceName, NewInterfaceName)

    def interfaceMove(self: Self, InterfaceName: str, NewDeviceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceMove(InterfaceName, NewDeviceName)

    def searchSet(self: Self, SetPattern: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.searchSet(SetPattern)

    def setInsert(self: Self, Set: SetInput | SetInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.setInsert(Set)

    def setRemove(self: Self, SetName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setRemove(SetName)

    def setSwitchPortTypeStatus(self: Self, SwitchName: str, PortName: str, SwitchPortTypeStatus: SwitchPortTypeStatus | SwitchPortTypeStatusDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.setSwitchPortTypeStatus(SwitchName, PortName, SwitchPortTypeStatus)

    def setSwitchPortMedium(self: Self, SwitchName: str, PortName: str, PortMedium: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setSwitchPortMedium(SwitchName, PortName, PortMedium)

    def setSwitchPortService(self: Self, SwitchName: str, PortName: str, Service: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.setSwitchPortService(SwitchName, PortName, Service)

    def getSwitchPortTypeStatus(self: Self, SwitchName: str, PortName: str) -> SwitchPortTypeStatus:
        self._confirm_authenticated()
        return self.client.service.getSwitchPortTypeStatus(SwitchName, PortName)

    def searchNetNameTable(self: Self, NetName: str) -> ArrayOfNetNameTuple:
        self._confirm_authenticated()
        return self.client.service.searchNetNameTable(NetName)

    def deviceAddLogicalInterface(self: Self, DeviceName: str, LogicalInterface: LogicalInterfaceInput | LogicalInterfaceInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceAddLogicalInterface(DeviceName, LogicalInterface)

    def deviceRemoveLogicalInterface(self: Self, DeviceName: str, InterfaceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.deviceRemoveLogicalInterface(DeviceName, InterfaceName)

    def interfaceUpdateDescription(self: Self, InterfaceName: str, Description: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.interfaceUpdateDescription(InterfaceName, Description)

    def serviceUpdateDescription(self: Self, ServiceName: str, Description: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.serviceUpdateDescription(ServiceName, Description)

    def getServiceInfo(self: Self, ServiceName: str) -> ServiceInfo:
        self._confirm_authenticated()
        return self.client.service.getServiceInfo(ServiceName)

    def vmCreate(self: Self, VMDevice: DeviceInput | DeviceInputDict, VMCreateOptions: VMCreateOptions | VMCreateOptionsDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmCreate(VMDevice, VMCreateOptions)

    def vmMigrate(self: Self, VMName: str, NewParent: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmMigrate(VMName, NewParent)

    def vmUpdate(self: Self, DeviceName: str, DeviceInput: DeviceInput | DeviceInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmUpdate(DeviceName, DeviceInput)

    def vmDestroy(self: Self, VMName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmDestroy(VMName)

    def vmClusterGetInfo(self: Self, VMClusterName: str) -> VMClusterInfo:
        self._confirm_authenticated()
        return self.client.service.vmClusterGetInfo(VMClusterName)

    def vmClusterGetDevices(self: Self, VMClusterName: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.vmClusterGetDevices(VMClusterName)

    def vmGetInfo(self: Self, VMName: str) -> VMInfo:
        self._confirm_authenticated()
        return self.client.service.vmGetInfo(VMName)

    def vmGetClusterMembership(self: Self, DeviceName: str) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.vmGetClusterMembership(DeviceName)

    def vmSearchCluster(self: Self, VMClusterSearch: VMClusterSearch | VMClusterSearchDict) -> ArrayOfString:
        self._confirm_authenticated()
        return self.client.service.vmSearchCluster(VMClusterSearch)

    def vmAddInterface(self: Self, VMName: str, InterfaceName: str, VMClusterName: str, VMInterfaceOptions: VMInterfaceOptions | VMInterfaceOptionsDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmAddInterface(VMName, InterfaceName, VMClusterName, VMInterfaceOptions)

    def vmRemoveInterface(self: Self, VMName: str, InterfaceName: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmRemoveInterface(VMName, InterfaceName)

    def vmMoveInterface(self: Self, VMName: str, InterfaceName: str, VMClusterName: str, VMInterfaceOptions: VMInterfaceOptions | VMInterfaceOptionsDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmMoveInterface(VMName, InterfaceName, VMClusterName, VMInterfaceOptions)

    def vmAddCard(self: Self, VMName: str, InterfaceCard: InterfaceCard | InterfaceCardDict) -> str:
        self._confirm_authenticated()
        return self.client.service.vmAddCard(VMName, InterfaceCard)

    def vmRemoveCard(self: Self, VMName: str, HardwareAddress: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.vmRemoveCard(VMName, HardwareAddress)

    def dnsZoneUpdate(self: Self, Zone: str, DnsZoneOptions: DnsZoneOptions | DnsZoneOptionsDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.dnsZoneUpdate(Zone, DnsZoneOptions)

    def dnsDelegatedSearch(self: Self, Search: str) -> ArrayOfDNSDelegatedEntry:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedSearch(Search)

    def dnsDelegatedGetByNameView(self: Self, Domain: str, View: str) -> DNSDelegatedEntry:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedGetByNameView(Domain, View)

    def dnsDelegatedAdd(self: Self, DNSDelegatedInput: DNSDelegatedInput | DNSDelegatedInputDict) -> bool:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedAdd(DNSDelegatedInput)

    def dnsDelegatedListKeys(self: Self) -> ArrayOfDNSDelegatedKey:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedListKeys()

    def dnsDelegatedRemove(self: Self, Domain: str, View: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedRemove(Domain, View)

    def dnsDelegatedAliasAdd(self: Self, Domain: str, View: str, Alias: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedAliasAdd(Domain, View, Alias)

    def dnsDelegatedAliasRemove(self: Self, Domain: str, View: str, Alias: str) -> bool:
        self._confirm_authenticated()
        return self.client.service.dnsDelegatedAliasRemove(Domain, View, Alias)


"""Generated TypedDict schemas for the LanDB SOAP API.

Generated from: https://network.cern.ch/sc/soap/soap.fcgi?v=6&WSDL
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypedDict

import suds.sudsobject  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from datetime import datetime


class DeviceInput(suds.sudsobject.Object):
    DeviceName: str
    Location: Location
    Zone: str | None
    Manufacturer: str
    Model: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem
    InventoryNumber: str | None
    LandbManagerPerson: PersonInput | None
    ResponsiblePerson: PersonInput
    UserPerson: PersonInput | None
    HCPResponse: bool | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class DeviceInputDict(TypedDict, total=False):
    DeviceName: str
    Location: Location | LocationDict
    Zone: str | None
    Manufacturer: str
    Model: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem | OperatingSystemDict
    InventoryNumber: str | None
    LandbManagerPerson: PersonInput | PersonInputDict | None
    ResponsiblePerson: PersonInput | PersonInputDict
    UserPerson: PersonInput | PersonInputDict | None
    HCPResponse: bool | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class DeviceInfo(suds.sudsobject.Object):
    DeviceName: str
    Location: Location | None
    Zone: str | None
    Status: str
    Manufacturer: str
    Model: str
    GenericType: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem
    InventoryNumber: str | None
    StartDate: Time | None
    EndDate: Time | None
    LandbManagerPerson: Person | None
    ResponsiblePerson: Person | None
    UserPerson: Person | None
    NetworkInterfaceCards: ArrayOfInterfaceCards | None
    Interfaces: ArrayOfInterfaces | None
    HCPResponse: bool
    Blocked: Blocking | None
    LastChangeDate: Time | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class DeviceInfoDict(TypedDict, total=False):
    DeviceName: str
    Location: Location | LocationDict | None
    Zone: str | None
    Status: str
    Manufacturer: str
    Model: str
    GenericType: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem | OperatingSystemDict
    InventoryNumber: str | None
    StartDate: Time | TimeDict | None
    EndDate: Time | TimeDict | None
    LandbManagerPerson: Person | PersonDict | None
    ResponsiblePerson: Person | PersonDict | None
    UserPerson: Person | PersonDict | None
    NetworkInterfaceCards: ArrayOfInterfaceCards | ArrayOfInterfaceCardsDict | None
    Interfaces: ArrayOfInterfaces | ArrayOfInterfacesDict | None
    HCPResponse: bool
    Blocked: Blocking | BlockingDict | None
    LastChangeDate: Time | TimeDict | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class DeviceBasicInfo(suds.sudsobject.Object):
    DeviceName: str
    Location: Location | None
    Zone: str | None
    Status: str
    Manufacturer: str
    Model: str
    GenericType: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem
    InventoryNumber: str | None
    StartDate: Time | None
    EndDate: Time | None
    LandbManagerPerson: Person | None
    ResponsiblePerson: Person | None
    UserPerson: Person | None
    HCPResponse: bool
    LastChangeDate: Time | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class DeviceBasicInfoDict(TypedDict, total=False):
    DeviceName: str
    Location: Location | LocationDict | None
    Zone: str | None
    Status: str
    Manufacturer: str
    Model: str
    GenericType: str
    Description: str | None
    Tag: str | None
    SerialNumber: str | None
    OperatingSystem: OperatingSystem | OperatingSystemDict
    InventoryNumber: str | None
    StartDate: Time | TimeDict | None
    EndDate: Time | TimeDict | None
    LandbManagerPerson: Person | PersonDict | None
    ResponsiblePerson: Person | PersonDict | None
    UserPerson: Person | PersonDict | None
    HCPResponse: bool
    LastChangeDate: Time | TimeDict | None
    IPv6Ready: bool | None
    ManagerLocked: bool | None


class Location(suds.sudsobject.Object):
    Building: str
    Floor: str
    Room: str


class LocationDict(TypedDict, total=False):
    Building: str
    Floor: str
    Room: str


class OperatingSystem(suds.sudsobject.Object):
    Name: str
    Version: str


class OperatingSystemDict(TypedDict, total=False):
    Name: str
    Version: str


class InterfaceCard(suds.sudsobject.Object):
    HardwareAddress: str
    CardType: str


class InterfaceCardDict(TypedDict, total=False):
    HardwareAddress: str
    CardType: str


class InterfaceInformation(suds.sudsobject.Object):
    ConnectedToSC: bool | None
    Name: str
    IPAddress: str
    ServiceName: str
    SecurityClass: str
    InternetConnectivity: bool
    SubnetMask: str | None
    DefaultGateway: str | None
    NameServers: ArrayOfString | None
    BelongsToSets: ArrayOfString | None
    TimeServers: ArrayOfString | None
    IPv6Address: str
    IPv6NetMask: int
    IPv6NameServers: ArrayOfString | None
    IPv6TimeServers: ArrayOfString | None
    IPv6DefaultGateway: str | None
    IPAliases: ArrayOfString | None
    BoundInterfaceCard: InterfaceCard | None
    Outlet: Outlet | None
    RackName: str | None
    Description: str | None
    NetworkDomainName: str
    Medium: str
    ReverseTelnet: ReverseTelnet | None


class InterfaceInformationDict(TypedDict, total=False):
    ConnectedToSC: bool | None
    Name: str
    IPAddress: str
    ServiceName: str
    SecurityClass: str
    InternetConnectivity: bool
    SubnetMask: str | None
    DefaultGateway: str | None
    NameServers: ArrayOfString | None
    BelongsToSets: ArrayOfString | None
    TimeServers: ArrayOfString | None
    IPv6Address: str
    IPv6NetMask: int
    IPv6NameServers: ArrayOfString | None
    IPv6TimeServers: ArrayOfString | None
    IPv6DefaultGateway: str | None
    IPAliases: ArrayOfString | None
    BoundInterfaceCard: InterfaceCard | InterfaceCardDict | None
    Outlet: Outlet | OutletDict | None
    RackName: str | None
    Description: str | None
    NetworkDomainName: str
    Medium: str
    ReverseTelnet: ReverseTelnet | ReverseTelnetDict | None


class Person(suds.sudsobject.Object):
    Name: str
    FirstName: str
    Department: str | None
    Group: str | None
    Email: str | None
    Phone: str | None
    CCID: int | None


class PersonDict(TypedDict, total=False):
    Name: str
    FirstName: str
    Department: str | None
    Group: str | None
    Email: str | None
    Phone: str | None
    CCID: int | None


class PersonInput(suds.sudsobject.Object):
    Name: str | None
    FirstName: str | None
    Department: str | None
    Group: str | None
    PersonID: int | None


class PersonInputDict(TypedDict, total=False):
    Name: str | None
    FirstName: str | None
    Department: str | None
    Group: str | None
    PersonID: int | None


class Outlet(suds.sudsobject.Object):
    ID: str
    FANOUT: bool


class OutletDict(TypedDict, total=False):
    ID: str
    FANOUT: bool


class OutletLocation(suds.sudsobject.Object):
    Location: Location
    Outlet: Outlet


class OutletLocationDict(TypedDict, total=False):
    Location: Location | LocationDict
    Outlet: Outlet | OutletDict


class ReverseTelnet(suds.sudsobject.Object):
    Data: str | None
    Port: str | None
    ServiceName: str | None


class ReverseTelnetDict(TypedDict, total=False):
    Data: str | None
    Port: str | None
    ServiceName: str | None


class Time(suds.sudsobject.Object):
    TimeUTC: datetime | None
    unixtime: int | None


class TimeDict(TypedDict, total=False):
    TimeUTC: datetime | None
    unixtime: int | None


class Blocking(suds.sudsobject.Object):
    By: Person
    Date: Time
    Reason: str
    UnblockRole: str


class BlockingDict(TypedDict, total=False):
    By: Person | PersonDict
    Date: Time | TimeDict
    Reason: str
    UnblockRole: str


class DeviceSearch(suds.sudsobject.Object):
    Name: str | None
    Surname: str | None
    FirstName: str | None
    Location: Location | None
    OutletID: str | None
    Tag: str | None
    SerialNumber: str | None
    InventoryNumber: str | None
    HardwareAddress: str | None
    IPAddress: str | None
    RackName: str | None
    PersonID: int | None
    Domain: str | None
    ResponsibleDepGroup: str | None
    UserResponsibleDepGroup: str | None
    OperatingSystem: str | None
    LastChangeDate: datetime | None
    LastActiveDate: datetime | None


class DeviceSearchDict(TypedDict, total=False):
    Name: str | None
    Surname: str | None
    FirstName: str | None
    Location: Location | LocationDict | None
    OutletID: str | None
    Tag: str | None
    SerialNumber: str | None
    InventoryNumber: str | None
    HardwareAddress: str | None
    IPAddress: str | None
    RackName: str | None
    PersonID: int | None
    Domain: str | None
    ResponsibleDepGroup: str | None
    UserResponsibleDepGroup: str | None
    OperatingSystem: str | None
    LastChangeDate: datetime | None
    LastActiveDate: datetime | None


class BulkInterface(suds.sudsobject.Object):
    InterfaceName: str | None
    IPAliases: ArrayOfString | None
    Location: Location
    OutletLabel: str
    SecurityClass: str
    InternetConnectivity: bool
    Medium: str
    SwitchName: str
    PortNumber: str
    CableNumber: str
    IP: str | None
    IPv6: str | None
    ServiceName: str | None


class BulkInterfaceDict(TypedDict, total=False):
    InterfaceName: str | None
    IPAliases: ArrayOfString | None
    Location: Location | LocationDict
    OutletLabel: str
    SecurityClass: str
    InternetConnectivity: bool
    Medium: str
    SwitchName: str
    PortNumber: str
    CableNumber: str
    IP: str | None
    IPv6: str | None
    ServiceName: str | None


class BulkInterfaceAuto(suds.sudsobject.Object):
    InterfaceName: str | None
    IPAliases: ArrayOfString | None
    Location: Location
    OutletLabel: str
    SecurityClass: str
    InternetConnectivity: bool
    Medium: str
    SwitchName: str
    PortNumber: str
    CableNumber: str
    IP: str | None
    IPv6: str | None
    ServiceName: str | None
    BindHardwareAddress: str | None


class BulkInterfaceAutoDict(TypedDict, total=False):
    InterfaceName: str | None
    IPAliases: ArrayOfString | None
    Location: Location | LocationDict
    OutletLabel: str
    SecurityClass: str
    InternetConnectivity: bool
    Medium: str
    SwitchName: str
    PortNumber: str
    CableNumber: str
    IP: str | None
    IPv6: str | None
    ServiceName: str | None
    BindHardwareAddress: str | None


class BulkMoveOptions(suds.sudsobject.Object):
    PreserveIP: bool


class BulkMoveOptionsDict(TypedDict, total=False):
    PreserveIP: bool


class Auth(suds.sudsobject.Object):
    token: str


class AuthDict(TypedDict, total=False):
    token: str


class SetInfo(suds.sudsobject.Object):
    ID: int
    Name: str
    Domain: str | None
    ResponsiblePerson: Person
    Description: str
    ProjectUrl: str | None
    Type: str
    Addresses: ArrayOfString | None
    Services: ArrayOfString | None
    Sets: ArrayOfString | None


class SetInfoDict(TypedDict, total=False):
    ID: int
    Name: str
    Domain: str | None
    ResponsiblePerson: Person | PersonDict
    Description: str
    ProjectUrl: str | None
    Type: str
    Addresses: ArrayOfString | None
    Services: ArrayOfString | None
    Sets: ArrayOfString | None


class SwitchPort(suds.sudsobject.Object):
    Name: str
    ServiceName: str
    Medium: str
    Type: str
    Status: str
    InUse: bool
    Devices: ArrayOfString | None
    Terminals: ArrayOfString | None


class SwitchPortDict(TypedDict, total=False):
    Name: str
    ServiceName: str
    Medium: str
    Type: str
    Status: str
    InUse: bool
    Devices: ArrayOfString | None
    Terminals: ArrayOfString | None


class SwitchPortTypeStatus(suds.sudsobject.Object):
    Type: str
    Status: str


class SwitchPortTypeStatusDict(TypedDict, total=False):
    Type: str
    Status: str


class InetInfo(suds.sudsobject.Object):
    HostName: str
    HardwareAddress: str
    IP: str
    NetAddress: str
    Mask: str
    GatewayAddress: str


class InetInfoDict(TypedDict, total=False):
    HostName: str
    HardwareAddress: str
    IP: str
    NetAddress: str
    Mask: str
    GatewayAddress: str


class Connection(suds.sudsobject.Object):
    InterfaceName: str
    SwitchName: str
    SwitchPort: str


class ConnectionDict(TypedDict, total=False):
    InterfaceName: str
    SwitchName: str
    SwitchPort: str


class ObservedSwitchConnection(suds.sudsobject.Object):
    SwitchName: str
    SwitchPort: str
    HardwareAddress: str


class ObservedSwitchConnectionDict(TypedDict, total=False):
    SwitchName: str
    SwitchPort: str
    HardwareAddress: str


class SetInput(suds.sudsobject.Object):
    Name: str
    Domain: str
    ResponsiblePerson: PersonInput
    Description: str
    ProjectUrl: str | None
    Type: str


class SetInputDict(TypedDict, total=False):
    Name: str
    Domain: str
    ResponsiblePerson: PersonInput | PersonInputDict
    Description: str
    ProjectUrl: str | None
    Type: str


class NetNameTuple(suds.sudsobject.Object):
    DeviceName: str
    InterfaceName: str
    IP: str
    IPv6: str
    Alias: str | None


class NetNameTupleDict(TypedDict, total=False):
    DeviceName: str
    InterfaceName: str
    IP: str
    IPv6: str
    Alias: str | None


class LogicalInterfaceInput(suds.sudsobject.Object):
    InterfaceName: str
    ServiceName: str
    SecurityClass: str
    IP: str | None
    IPv6: str | None
    InternetConnectivity: bool | None


class LogicalInterfaceInputDict(TypedDict, total=False):
    InterfaceName: str
    ServiceName: str
    SecurityClass: str
    IP: str | None
    IPv6: str | None
    InternetConnectivity: bool | None


class ServiceInfo(suds.sudsobject.Object):
    Name: str
    Primary: str | None
    AddressIni: str
    AddressEnd: str
    AddressCount: int
    SubnetMask: str
    DefaultGateway: str | None
    NameServers: ArrayOfString | None
    TimeServers: ArrayOfString | None
    Mediums: ArrayOfString | None
    NetworkDomain: str | None
    Description: str | None
    UserIPTotal: int
    UserIPFree: int
    IPv6Network: str
    IPv6NetMask: int
    IPv6DefaultGateway: str | None
    IPv6NameServers: ArrayOfString | None
    IPv6TimeServers: ArrayOfString | None
    Secondaries: ArrayOfString | None


class ServiceInfoDict(TypedDict, total=False):
    Name: str
    Primary: str | None
    AddressIni: str
    AddressEnd: str
    AddressCount: int
    SubnetMask: str
    DefaultGateway: str | None
    NameServers: ArrayOfString | None
    TimeServers: ArrayOfString | None
    Mediums: ArrayOfString | None
    NetworkDomain: str | None
    Description: str | None
    UserIPTotal: int
    UserIPFree: int
    IPv6Network: str
    IPv6NetMask: int
    IPv6DefaultGateway: str | None
    IPv6NameServers: ArrayOfString | None
    IPv6TimeServers: ArrayOfString | None
    Secondaries: ArrayOfString | None


class DnsZoneOptions(suds.sudsobject.Object):
    Internal: bool | None
    External: bool | None


class DnsZoneOptionsDict(TypedDict, total=False):
    Internal: bool | None
    External: bool | None


class VMCreateOptions(suds.sudsobject.Object):
    VMParent: str | None


class VMCreateOptionsDict(TypedDict, total=False):
    VMParent: str | None


class VMInterfaceOptions(suds.sudsobject.Object):
    IP: str | None
    IPv6: str | None
    ServiceName: str | None
    InternetConnectivity: str | None
    AddressType: str | None
    BindHardwareAddress: str | None


class VMInterfaceOptionsDict(TypedDict, total=False):
    IP: str | None
    IPv6: str | None
    ServiceName: str | None
    InternetConnectivity: str | None
    AddressType: str | None
    BindHardwareAddress: str | None


class VMInfo(suds.sudsobject.Object):
    Name: str
    IsVM: bool
    VMParent: str | None
    VMGuestList: ArrayOfString | None


class VMInfoDict(TypedDict, total=False):
    Name: str
    IsVM: bool
    VMParent: str | None
    VMGuestList: ArrayOfString | None


class VMClusterInfo(suds.sudsobject.Object):
    ID: int
    Name: str
    Description: str | None
    ResponsiblePerson: Person | None
    Services: ArrayOfString | None


class VMClusterInfoDict(TypedDict, total=False):
    ID: int
    Name: str
    Description: str | None
    ResponsiblePerson: Person | PersonDict | None
    Services: ArrayOfString | None


class IPMIOptions(suds.sudsobject.Object):
    UseDeviceName: bool | None


class IPMIOptionsDict(TypedDict, total=False):
    UseDeviceName: bool | None


class VMClusterSearch(suds.sudsobject.Object):
    ClusterName: str | None
    Surname: str | None
    FirstName: str | None


class VMClusterSearchDict(TypedDict, total=False):
    ClusterName: str | None
    Surname: str | None
    FirstName: str | None


class BOOTPInfo(suds.sudsobject.Object):
    Server: str | None
    ImagePath: str | None


class BOOTPInfoDict(TypedDict, total=False):
    Server: str | None
    ImagePath: str | None


class DNSDelegatedInput(suds.sudsobject.Object):
    Domain: str
    View: str
    KeyName: str
    Description: str
    UserDescription: str


class DNSDelegatedInputDict(TypedDict, total=False):
    Domain: str
    View: str
    KeyName: str
    Description: str
    UserDescription: str


class DNSDelegatedEntry(suds.sudsobject.Object):
    ID: int | None
    Domain: str
    View: str
    KeyName: str
    Description: str | None
    UserDescription: str | None
    Aliases: ArrayOfString | None


class DNSDelegatedEntryDict(TypedDict, total=False):
    ID: int | None
    Domain: str
    View: str
    KeyName: str
    Description: str | None
    UserDescription: str | None
    Aliases: ArrayOfString | None


class DNSDelegatedKey(suds.sudsobject.Object):
    ID: int | None
    KeyName: str
    Responsible: Person | None


class DNSDelegatedKeyDict(TypedDict, total=False):
    ID: int | None
    KeyName: str
    Responsible: Person | PersonDict | None


ArrayOfDeviceInfo: TypeAlias = list[DeviceInfo]

ArrayOfDeviceInfoDict: TypeAlias = list[DeviceInfoDict]

ArrayOfInterfaceCards: TypeAlias = list[InterfaceCard]

ArrayOfInterfaceCardsDict: TypeAlias = list[InterfaceCardDict]

ArrayOfString: TypeAlias = list[str]

ArrayOfInterfaces: TypeAlias = list[InterfaceInformation]

ArrayOfInterfacesDict: TypeAlias = list[InterfaceInformationDict]

ArrayOfBulkInterfaces: TypeAlias = list[BulkInterface]

ArrayOfBulkInterfacesDict: TypeAlias = list[BulkInterfaceDict]

ArrayOfBulkInterfacesAuto: TypeAlias = list[BulkInterfaceAuto]

ArrayOfBulkInterfacesAutoDict: TypeAlias = list[BulkInterfaceAutoDict]

ArrayOfSwitchPort: TypeAlias = list[SwitchPort]

ArrayOfSwitchPortDict: TypeAlias = list[SwitchPortDict]

ArrayOfConnection: TypeAlias = list[Connection]

ArrayOfConnectionDict: TypeAlias = list[ConnectionDict]

ArrayOfObservedSwitchConnection: TypeAlias = list[ObservedSwitchConnection]

ArrayOfObservedSwitchConnectionDict: TypeAlias = list[ObservedSwitchConnectionDict]

ArrayOfInetInfo: TypeAlias = list[InetInfo]

ArrayOfInetInfoDict: TypeAlias = list[InetInfoDict]

ArrayOfNetNameTuple: TypeAlias = list[NetNameTuple]

ArrayOfNetNameTupleDict: TypeAlias = list[NetNameTupleDict]

ArrayOfDNSDelegatedEntry: TypeAlias = list[DNSDelegatedEntry]

ArrayOfDNSDelegatedEntryDict: TypeAlias = list[DNSDelegatedEntryDict]

ArrayOfDNSDelegatedKey: TypeAlias = list[DNSDelegatedKey]

ArrayOfDNSDelegatedKeyDict: TypeAlias = list[DNSDelegatedKeyDict]

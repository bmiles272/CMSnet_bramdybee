# CMSNet Documentation

CMSNet software is used as a bridge between the CMS device database and the LanDB database (main CERN one). The code kept in the CMSNet gitlab repository (https://gitlab.cern.ch/cms-daq-sysadmins/cmsnet_ng.git) has been created to update the older CMSNet which ran on PERL scripts. The old CMSnet is here https://gitlab.cern.ch/cms-daq-sysadmins/cmsnet.git

New CMSNet has 5 main functions (same as old):
* Add: Add a device from the CMS database to the LanDB database.
* Remove: Delete an interface or device from the lanDB database.
* Check: Check for inconsistencies between the CMS and LanDB databases.
* Update: Similar to check function but gives the user the option to update the information. Only works one way, if data is different chnage comes from CMS database and is applied to lanDB.
* Extract: Extract devices within a domain from lanDB and build DHCP and DNS configuration files from the extracted devices.

Immediate changes that need to be made:
-- 

- Within CSVExtracttoDict.py the BulkInterface dictionary needs ipmi interface to be added in the presence of an IPMIMAC for each device. Currently this is taken into account in the add function by doing this logic there however this leaves problems for the delete, check and update functions as when we compare or try to detect all interfaces present the ipmi interface is not present (apologies I spotted this on my last day and did not have the time to make the edits). The logic for this should not be hard, it is done this way in the add function and this can be easily adapted to the csvextracttodict:
    - Detect whether an ipmi interface is not present in the csv files. In add function this is done in lines 34-36, when the class is initlialised and then called upon later in the code. This can be put directly into the bulkinterface function where other dicts can be called using self._function_. 
    - If ipmi is present then dont do the following steps as ipmi should be automatically created.
    - If ipmi not present in csv then search for an ipmimac in the serial files using the MACaddress dict function in csvextracttodict, done in line 83 in add function.
    -  If ipmimac present then all we need to do is takje the information from main device interface (the first one created) and chnage the name of the interface to include ipmi, this is done in lines 145-157 in add function.
- This should add ipmi interface to bulk interface list of interfaces. It will simplify the add logic and simplify the check function logic (lines 91-111) and update logic (lines 70-92).
- This will solve error in delete function which appeared on my last day, and solve missing interfaces in the check function.

client_bramdybee.py + bramdybee.py
--
**Code description:**

These two scripts work closely along isde eachother, the client file acts as a client interface to interact with the SOAP API while bramdybee.py handels authentication. Almost every fucntion or call made to SOAP requires authentication with a CERN privlidged account. 

When you create an instance of the LanDB class within client_bramdybee, it sets up the connection to the API using the URL provided and handles any issues with the XML format. If you give it a username and password, it will log you in and save a token that gets used for future requests. One function added on top of what was pulled from landybee client.py repo (https://gitlab.cern.ch/acc-adm/network/landybee.git), fillToken() function automatically fills the token if we are authorised on the bramdybee.py file.

Contains the BramDB class which handles automatic authentication. When you create an instance of bramDB, it sets up a connection to the LanDB client. If you provide a username and password, it immediately tries to authenticate and make sure there's a valid token ready to go.

The code has a few key methods for managing this token. The write_env method takes care of storing the token in a .env file, so you can easily save it and use it later without needing to log in again. The file_older_than_9half method is a little check to see if this .env file is older than 9.5 hours, which is important because the token only lasts for 10 hours. This gives you a 30-minute buffer to ensure the token is still good.

As for the authentication flow, if the .env file exists and the token inside is still valid, it grabs the token from there and uses it to log in via the filltoken method. But if the file is missing or the token has expired, the code prompts the user to enter their credentials, generates a new token, and then saves it back into the .env file for future use.

**Potential errors:**

Very occasionally when using along side CMSNet_ng_extract.py the script does not recognise the token and will give #BADAUTH error. Unable to understand why this occurs, if it occurs simply delete .env file and authorise again then it will work.

CSVExtracttoDict.py
--
**Description of code:**

Script which transforms the data from CMS CSV device files into python dictionaries. This is required for use next to the landybee functions as they often require a python dictionary input. For example, the deviceInsert function whihc requires a device_input dictionary, containing various device parameters. Some types require dictionaries within dictionaries, for example the DeviceInput requires a location 'dictionary' within it.

Within initiliasation of the class the csv files and dynamically read, domains and delimiters are defined and speed and medium keys are created. These are all used when extracting data from different csv files. The speed key will when eventually returned to original value have to be multiplied by 1000 to return to Gigabit per second (this is for intfspeed.cms dns file). The code creates the following dictionaries:
- Location Dictionary (location)
- Person Input Dictionary (PersonInput)
- Operating System Dictionary (OperatingSystem)
- Interface Card Dictionary (InterfaceCard)
- IPMI Interface Card Dictionary (IPMIinterfacecard)
- Device Input Dictionary (DeviceInput)
- Bulk Interface Dictionary (BulkInterface)
- MAC Addresses Dictionary (MACaddress)

It also returns the following lists:
- IP Alias List (IPAliasList)
- Interface Card List (CombinedInterfaceCards)
- Interface Names List (interface_list)
- Bulk Interfaces List (BulkInterface)

I am unsure whether all the functions are used somewhere however they all had a use at some point.

Difference between BulkInterface and Interfaces is that BulkInterface is in the format required by types.py, the interfaces fucntion simply lists the interfaces, info and their associated aliases (bulkinterface requires a list of aliases).

**Usage:**

Script is used in any place where we need to extract data from the CMS csv files. Therefore the Add, Delete, Check and Update use them (the extract should focus only on lanDB entries).


**Limitations:**

Any extra dictionaries that are required will be needed to created manually. Cannot see any reason why this would be needed now but might be possible.

Potential restructure to the BulkInterface call from CSVExtracttoDict.py, this dictionary only produces dictionaries of the interfaces mentioned in the csv files. However IPMI interfaces are not found if they do not have a different service as they are not listed. Taking into account the IPMIMAC at this point would allow the logic in the add, delete, check and update fucntion to be simplified. For example instead of generating the IPMI interface within the add_interface function it would already be in the extract bulk interface and therefore simplify the logic. Further the check function would now take into account the ipmi interfaces, which it did not previously (apologies I did not spot this until my last day).


CMSNet_ng_add.py
--
**Description of code:**

The purpose of the add function, as you might expect, is to add devices registered in the CMS CSV files into the lanDB database. The code does this in three steps. First, it adds the device information, including details like manufacturer, operating system, and the responsible person. Second, the device's network interface cards (NICs) are added. These are added only if the device has valid MAC addresses in the serial files, which relate a device's serial number to hardware addresses. If an IPMIMAC is present, an IPMI NIC is also added. From our CSV files, devices can have up to three NICs: OnboardMAC1, OnboardMAC2, and IPMIMAC. Lastly, the device's interfaces are added with information taken from interfaces.csv. Since types.py requires a location input for the interfaces, we set this equal to the device's location.

The interface logic is longer and not shown here. It checks switch information, and if the switch is occupied, it attempts a fanout method so that the device can still be added. Additionally, if an IPMIMAC is present, an IPMI interface is created.

By separating the device information, NICs, and interfaces, the add function sets a structure that the check and update functions can follow for easier analysis. While Landybee also provides a bulkAddDevice function that performs all three additions at once, if an error occurs while creating a device, it cancels the entire operation. This makes it difficult to pinpoint the source of the error. Separating the additions not only provides better structure but also makes troubleshooting easier.

**Usage:**

To use the add function, a user runs the script with the ```--add``` flag and specifies device names, like ```python3.11 cmsnet_ng/Landybee/CMSNet_ng_add.py device1 device2 --add```. This command triggers the cmsnet_add class to sequentially insert device information, add network interface cards, and handle bulk interfaces. If the ```--print-info``` flag is included, the script will also display detailed information about each device and its interfaces during the process.

**Limitations:**

Code is very much based on current structure of CSV files and is pretty inflexible with any changes. If the csv file structure is changed then code will have to be reevaluated.


CMSNet_ng_delete.py
--
**Description of code:**

The delete function, as expected, removes devices and interfaces from the lanDB database. The function starts by checking if the device exists in the lanDB database. If it does, the deletion process begins. Before every deletion, the user is prompted to confirm that they want to delete the device. There are two options within the code: deletion of specific interfaces or deletion of an entire device. If the user wants to delete specific interfaces, they are shown a list of interfaces and can select the one to be removed. If the entire device is removed, all interfaces are deleted, followed by the device information. This is because the device information cannot be deleted while leaving unattached interfaces. 

**Usage:**

To use the script, you’d run it from the command line, providing the device name and specifying what you want to do. For example, using the --delete-interface flag lets you delete a particular interface, while --delete removes the whole device. The script will prompt you for confirmation and interface choices as needed. Example; ```python3.11 cmsnet_ng/Landybee/CMSNet_ng_delete.py device1 device2 --delete (-y)```

The extra -y option allows user to bypass manual input and simply acceptsall deletions automatically.

**Future:**

The following italic comment was implemented just as I left, this works fine however without the improvement to bulkinterface (where impi interface is included in the presence of IPMIMAC) this will fail as without presence of ipmi interface in bulkinterface dictionary it wont delete all the interfaces and therefor wont be able to delete the device.
*Function '-y' should be added which forces yes input on all bulk deletions so any mass deletion does not require lots of manual input.*


CMSNet_ng_check.py
--
**Description of code:**

The cmsnet_check script is designed to compare device information between CMS CSV files and the lanDB CERN database. When executed, the script first verifies if the specified device exists in lanDB. If the device is found, it reads device details from the CSV files and fetches additional information from lanDB, such as interface details. The script then proceeds to flatten the returned dictionaries, normalise values, and compare device parameters, network interface cards, and device interfaces. The script relies largely on the structure determined in the add function: device info, NICs, interfaces.

Example of normalisation: LanDB returns ```room= 0001``` while our csv files give ```room= 1``` within location dictionary. Therefore we must normalise the lanDB room value for correct comparison.

By flatten dictionaries we mean flatten nested dictionaries. Example: {entry1: 1, entry2: {entry3: 3, entry4: 4}} turns into {entry1: 1, entry2.entry3: 3, entry2.entry4: 4}

**Usage:**

To use the script, run it from the command line with the device names you want to check. For example, if you want to compare data for a device named "DeviceA", you would execute:

```python3.11 cmsnet_ng/Landybee/CMSNet_ng_check.py DeviceA DeviceB --check (--verbose)```

This command initializes the comparison process, where the script will compare the device’s input parameters, network interface cards, and interfaces between the CMS CSV files and the lanDB database. The script will print any differences it finds for each aspect, allowing you to identify discrepancies.
Verbose function prints all the information at each stage in the check. If not included it only prints differences.
Note: many devices can be checked at once.

**Limitations:**

Code relies heavily on lanDB output data structure for comparison. 

**Future**

Verbose added before I left.
*Verbose to be added so that all the extra writing is not added and only the differences are printed.*

The check function currently does not detect missing interrfaces, however this should be simple enough: obtaining lists of interfaces present in each database if there are interfaces present which dont belong then report them to user.

CMSNet_ng_update.py
--
Description of code:

The update function builds on the check function. It identifies differences between devices in the lanDB and CMS databases, and for any discrepancies, the code prompts the user to accept or decline the change. The update function only modifies entries in lanDB, not the CMS database. Thus, CMS is treated as the source of truth. This holds true for all the previous functions as well. The reasoning behind this approach is that once the code is fully implemented and all functions are running correctly, the check and update functions will ensure the lanDB database is up to date before extracting DNS and DHCP information.

The update function follows the structure of the check function, taking its output and using various lanDB functions to modify values in NICs, device information, and interfaces. For NICs, the process involves unbinding and deleting the existing NIC, then creating and binding a new one.

Usage:

To use the script, run it from the command line with the device names you want to check. For example, if you want to compare data for a device named "DeviceA", you would execute:

```python3.11 cmsnet_ng/Landybee/CMSNet_ng_update.py DeviceA DeviceB --update```

Note: many devices can be updated at once.

Limitations:

Update function shares the limitations of the check function as they do virtually the same thing. Inflexible structure if lanDB chnage anything and also if csv files change.


Future:

Verbose function could be added in the same manner as the check function as currently it also prints all the infomration. Simple code additions.



CMSNet_ng_extract.py
--
Description of code:

The extract function is used to populate DNS and DHCP configuration files by retrieving data from the lanDB database. The code requires a domain from which to extract devices. The current valid domains are CMS and CMS904, but these can easily be updated in the code. Similarly, when searching for device interfaces within the domain, we need domain delimiters. These delimiters are defined at the start of the code and can also be easily changed. This is useful for when the device naming scheme changes in the near future.

When querying for all devices within a domain, the code obtains a list of device names. It then uses a lanDB function to retrieve device information for all listed devices. The CMS domain has roughly 4,200 devices, but the lanDB function can only handle 200 devices at a time. Therefore, the list is split into sets of 200, and the code iterates through them to obtain all the device information.

**DHCP:**

To generate the DHCP files we must obtain 5 attributes from each device: hardware address, IP address, subnet mask, broadcast address, and default gateway. Through some sort of logic 4 of these 5 are obtainable from the device information returned by lanDB, broadcast address is the only one obtained through some sort of function. However that does not mean that obtaining the other information is always trivial. 

The logic in the script always tries to look for hardware address first, it tries to obtain the MAC address associated to the device. However, the MAC addresses are found in the NICs which can be bounded to interfaces. Therefore the code looks through interfaces until it finds one it believes to be the 'main' device interface (often the interface name is a good indictator). If this is unachievable due to a different naming system or because there are no NICs bound to any interfaces then the script scans the NICs, if only one NIC exists then we know the hardware address for the device must exist in there. If more than one exists then currently the code has no way of determining the hardware address and it ignores the device. Once the hardware address is found the IP, subnet mask and default gateway are trivially defined.

Once all the parameters are obtained for a device we categorise the device, the device is categorised into one of four categories: cc8, dcs, juniper and misc. The misc file takes any devices that don't fit into the first three. The cc8 category requires specific Lunix operating system versions such as ALMA9. The dcs category is for devices that use Windows operating system. The juniper category is for devices who's manufacturer is Juniper, this is mainly for routers. These different categories are used as keys within a dictionary, where the device parameters obtained are elements of the dictionary. **Note when discussed in my final presentation it was discussed that some of these categories were to be removed for simplicity Marc Dobson has these meeting notes.**

The code also creates an ipmi-misc file which is for ipmi interfaces which have bound interface cards, as ipmi can have their own hardware addresses.

This whole process is iterated over all devices within the selected domain. The dictionary is then used to populate the different files.

**DNS:**

The DNS files are created differently to the DHCP files. Firstly we require all IP addresses from all interfaces for every device, which is relatively trivial to obtain. 

*Device to IP files:*
The code then begins to order the devices into subdomains, the subdomains are determined by the naming of the interface. All interfaces are named "DEVICE\_NAME - SUBDOMAIN - DOMAIN.CERN.CH" where sometimes if devices don't have any subdomain or domain these will be empty. In the case where no subdomain can be determined or there is no subdomain the devices are pushed into a 'cms' subdomain. Out of the large list of subdomains produced there are only a number of 'allowed' subdomains, the allowed domains are defined on line 47. The subdomains produced which are not in the list are also pushed to the 'cms' domain.

Once the subdomain is determined the device interfaces and their IP addresses are put into a dictionary, again, where the subdomains are the keys and tuples of interface and IP address are the elements. Files are then generated based on the subdomains.

*Reverse IP lookup files:*
The code also includes a reverse IP lookup. Reverse IP is created by splitting the IP address and switching the final two sections. The zone of the reverse IP is then determined by switching the first two sections of the IP address. This is done for all interfaces, the zone now acts as the subdomain and the reverse IP as the IP. Again files are filled based on zones.

*Alias, CNAME entries:*
The DNS files also require alias entries, also known as CNAME entries, for interfaces, in future these aliases are to be extracted alongside the rest of the device information. However, currently very few devices have alias on the lanDB database. In the current script the alias are taken from the aliases2.csv file which is copied form the old CMSnet repository. However, once all the aliases have been transferred to the lanDB database this part of the code is to be commented out.

Improvements still to be made include:
--

Updates in the logic surrounding the DHCP and DNS files: while functional do not capture all the devices in the CMS domain. Logic for the DHCP configuration files should include the devices where hardware addresses are currently not able to be found due to non-trivial interface names as well as situations in which multiple NICs stop the code from finding an exact hardware address for the device. Once this is done, since the current code provides markers of which devices were ignored, the devices which are still rejected should be analysed in a case by case basis for any exceptions.

Streamlining the processing time of the creation of DNS and DHCP files: it took the old CMSnet roughly 10 minutes to produce all the files. The new CMSnet takes around 5 minutes, that is a 50\% decrease, however I believe this can be reduced further through the use of thread-pool executors or equivalent in python which parallelise executions of API calls, such calls should be made when getting the device information for large numbers of devices (CMSnet\_ng\_extract.py). It is believed these large calls to lanDB is what is causing a bottle neck and cost the most computing time with each batch of 200 devices taking roughly 15 seconds. Therefore running them in parallel should reduce the overall time.
 
intfspeed.cms and auto-ifconfig.cms files to be created in the extract function. The intfspeed.cms file registers the speed and IP of each device, these speeds shoudl be taken from lanDB database when extracting device information. The speeds can then be converted from the GIGABIT format into numbers as done in the CSVExtracttoDict.py script using keys. The autoi-ifconfig.cms file registers the network routes of all the interfaces within a device and the default gateway others must use to reach the interface. This information can be found in the networks and network\_routes csv files.

Comparison of output between current CMSnet and new CMSnet to ensure the output of the scripts is identical. It allows us to determine any faults in the scripts and ensures there are no fails once the scripts are set for deployment.

Smooth updates of DNS and DHCP files would mean DNS and DHCP files do not have to be reproduced every time they are updated. Instead any updated or new devices are detected and added to the already existing files, this would hugely reduce any computing time.

Contact:
-- 
If you have any questions or comments about the code dicussed in the git repo please do not hesistate to email me at brammiles@gmail.com

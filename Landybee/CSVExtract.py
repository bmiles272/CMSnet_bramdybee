import pandas as pd

class CMSNetCSVExtract:

    def __init__(self) -> None:
        self.devices_columns = ['Device', 'Serial', 'Zone', 'Manufacturer', 'model', 'Description', 'Tag', 'OS', 'OSversion', 'building', 'floor', 'room', 'Responsible', 'MainUser', 'ITDHCP']
        self.aliases_columns = ['Device','IFName','Alias']
        self.interfaces_columns = ['Device', 'IFName', 'LinuxIF', 'ServiceName', 'Switch', 'Port', 'Cable', 'Speed']
        self.networks_routes_columns =  ['SourceNetName', 'DestNetName', 'GatewayIP']
        self.networks_columns = ['NetName', 'ServiceName', 'MTU']
        self.switches_special_ports_columns = ['Switch', 'Port', 'Speed', 'PortType']

    def importfile(self, csvname):
        filepath = f'data/cms/{csvname}.csv'
        csvfile = pd.read_csv(filepath, comment='#')
        return csvfile

    def extractcolumns(self, csv: str, columnnames):
        csvfile = self.importfile(csv)
        self.checkcsv(csvfile, columnnames)

        for index in range(len(csvfile.columns)):
            variable_name = columnnames[index]
            column_data = csvfile.iloc[:, index].tolist()
            globals()[variable_name] = column_data
        return print(f'You can now call the data by variable names: {columnnames}')
    
    def extractelement(self, csv: str, indx_row, indx_col):
        csvfile = self.importfile(csv)
        extracted_elements = csvfile.iloc[indx_row, indx_col]
        return extracted_elements

    def extractrow(self, csv: str, rowindex):
        csvfile = self.importfile(csv)
        extractedrow = csvfile.iloc[rowindex, :]
        return extractedrow
    
hey = CMSNetCSVExtract()
d = hey.importfile('devices')
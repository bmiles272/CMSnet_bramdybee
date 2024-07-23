import pandas as pd

class CMSNetCSVManager:

    def __init__(self) -> None:
        self.devices_columns = ['Device', 'Serial', 'Zone', 'Manufacturer', 'model', 'Description', 'Tag', 'OS', 'OSversion', 'building', 'floor', 'room', 'Responsible', 'MainUser']
        self.aliases_columns = ['Device','IFName','Alias']
        self.interfaces_columns = ['Device', 'IFName', 'LinuxIF', 'ServiceName', 'Switch', 'Port', 'Cable', 'Speed']
        self.networks_routes_columns =  ['SourceNetName', 'DestNetName', 'GatewayIP']
        self.networks_columns = ['NetName', 'ServiceName', 'MTU']
        self.switches_special_ports_columns = ['Switch', 'Port', 'Speed', 'PortType']


    def importfile(self, csvname):
        filepath = f'data/cms/{csvname}.csv'
        csvfile = pd.read_csv(filepath, comment='#', header=None)
        return csvfile

    def extractcolumns(self, csvfile, columnnames):

        if len(csvfile.columns) != len(columnnames):
            raise ValueError("The number of column names does not match the number of columns in the csv file.")


        data_dict = {}
        for index in range(len(csvfile.columns)):
            variable_name = columnnames[index]
            column_data = csvfile.iloc[:, index].tolist()
            data_dict[variable_name] = column_data

        for key, value in data_dict.items():
            setattr(self, key, value)

        print(f'You can now call the data by variable names: {columnnames}')
        return data_dict
        # for index in range(len(csvfile.columns)):
        #     variable_name = columnnames[index]
        #     column_data = csvfile.iloc[:, index].tolist()
        #     globals()[variable_name] = column_data

        # return print(f'You can now call the data by variable names: {columnnames}')

hey = CMSNetCSVManager()

aliasesdata = hey.extractcolumns(hey.importfile('aliases'), hey.aliases_columns)
print(IFName)
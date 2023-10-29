from App import ConsoleApp

if __name__ == '__main__':
    version = '0.1'
    brand = f"""
     ____        _           ____      _             _   _ _            
    |  _ \  __ _| |_ __ _   / ___|__ _| |_          | | | (_)_ __ __  __
    | | | |/ _` | __/ _` | | |   / _` | __|  _____  | |_| | | '_ \\ \/ /
    | |_| | (_| | || (_| | | |__| (_| | |_  |_____| |  _  | | | | |>  < 
    |____/ \__,_|\__\__,_|  \____\__,_|\__|         |_| |_|_|_| |_/_/\_\                                                                                                                                                                                                                                                                
    Data Console v{version} (请输入help查看可用命令)
    """
    print(brand)
    app = ConsoleApp.ConsoleApp()
    app.cmdloop()

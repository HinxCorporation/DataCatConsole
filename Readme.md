# DataCat Console version

     ____        _           ____      _             _   _ _
    |  _ \  __ _| |_ __ _   / ___|__ _| |_          | | | (_)_ __ __  __
    | | | |/ _` | __/ _` | | |   / _` | __|  _____  | |_| | | '_ \ \/ /
    | |_| | (_| | || (_| | | |__| (_| | |_  |_____| |  _  | | | | |>  <
    |____/ \__,_|\__\__,_|  \____\__,_|\__|         |_| |_|_|_| |_/_/\_\                                           
    
    Data Console v0.1 (请输入help查看可用命令)

## Descriptions

> A project going to manage large file system , index files and make monitor , basic services for media manage and file manage.


## Similar project

File Monitor [Link]("https://github.com/HinxCorporation/FileMonitor")

## Difference

- hide default option
- clearly reference
- output to mysql database

## How to start


- init cmds

```shell
python -m venv venv
```

- active venv

```shell
.\venv\Scripts\Activate.ps1
```

- install requirements

```shell
pip install -r requirements.txt
```

- go to console

```
python main.py
```

- console


```cmd2
DataCat CLI>> help
╒══════════════╤═══════════════════════════════════════════════════════════════════╕
│ 可用的指令     │ 描述                                                              
╞══════════════╪═══════════════════════════════════════════════════════════════════╡
│ exhelp       │ 查看原版help (使用所有原版arg)                                    	
├──────────────┼───────────────────────────────────────────────────────────────────┤
│ quit         │ Exit this application                                             
├──────────────┼───────────────────────────────────────────────────────────────────┤
│ rebuild      │ 从config中读取folders,并且为他们重新构建数据库,插入到指定的sql中. 		 
│              │ 需要配置分表大小,若文件夹超过大小*3,则按照配置的大小进行分表处理  			 
│              │ ---默认规则为继续递归下级目录创建子数据库                     			
╘══════════════╧═══════════════════════════════════════════════════════════════════╛
DataCat CLI>>
```


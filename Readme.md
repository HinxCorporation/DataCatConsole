# DataCat Console version

     ____        _           ____      _             _   _ _
    |  _ \  __ _| |_ __ _   / ___|__ _| |_          | | | (_)_ __ __  __
    | | | |/ _` | __/ _` | | |   / _` | __|  _____  | |_| | | '_ \ \/ /
    | |_| | (_| | || (_| | | |__| (_| | |_  |_____| |  _  | | | | |>  <
    |____/ \__,_|\__\__,_|  \____\__,_|\__|         |_| |_|_|_| |_/_/\_\
    
    Data Console v0.1 (请输入help查看可用命令)

## Descriptions

> A project going to manage large file system , index files and make monitor , basic services for media manage and file
> manage.

## History

#### 2023年10月30日21:55:08

1. 新增若干指令
2. `ls_rebuild` 预览需要重建数据库的文件夹列表,以及其将会存放的数据库
3. `ls_rules` 预览重建数据库列表越过规则
4. `test_conn` 链接mysql测试
5. `test_count` 预览文件夹文件计数 (已经计数过的文件夹本次运行将会使用缓存记录 ,
   配合大文件夹分表功能给大文件夹分为子table)
6. `folder_paths.txt` 新增feature, 使用&开始的文件夹将会被配置为拆分, 例如`&/dir/large_folder/`
   子文件夹有`foldera`,`folderb`, 则改记录会被拆分为 `/dir/large_folder/foldera` 和`/dir/large_folder/folderb` , 其他以此类推

![snapshot](https://github.com/HinxCorporation/DataCatConsole/blob/71628c467b24d95f682d26243d2f326c2baf77c2/Readme.assets/image-20231030215510957.png)

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

## TODO

- [ ] Create a table while db is finished . record its storage id . view id actually.
- [ ] View ID divide into 10 level , from level 1 to level 11
- [ ] Compare it if it needs to update .
- [ ] database to hash name
- [ ] access monitor part to this sys.


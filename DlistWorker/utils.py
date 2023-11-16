import re

dlist_rule = re.compile(r'(.+?)_(\d+)\.dlist$')


def get_is_rebuilds(file: str) -> bool:
    """
    是否重建内容
    :param file:
    :return:
    """
    return file.startswith('rebuild')


def get_time_index(file: str) -> int:
    """
    获取文件名中的时间片段.
    :param file:
    :return:
    """
    su, cmd, ts = extract_cmd_and_timestamp(file)
    if su:
        return int(ts)
    return 0


def extract_cmd_and_timestamp(filename) -> (bool, str, str):
    """
    将dlist文件名切分为cmd + timestamp
    :param filename:
    :return:
    """
    if filename.endswith(".dlist"):
        # Extract the command and timestamp using regular expressions
        match = dlist_rule.match(filename)
        if match:
            cmd = match.group(1)  # Extract the command
            timestamp = match.group(2)  # Extract the timestamp
            return True, cmd, timestamp
    return False, None, None

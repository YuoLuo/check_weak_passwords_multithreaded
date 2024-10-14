import mysql.connector
from mysql.connector import Error
import threading
import argparse

# 数据库连接配置模板
db_config_template = {
    'host': None,  # 将在运行时设置
    'user': None,  # 将在运行时设置
    'password': None,
}


# 读取文件内容
def load_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


# 检查弱口令
def check_credentials(ip, username, password):
    db_config = db_config_template.copy()
    db_config['host'] = ip
    db_config['user'] = username
    db_config['password'] = password

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print(f"成功连接: {ip} - 用户: {username} - 密码: {password}")
            connection.close()
    except Error as e:
        if "Access denied" in str(e):
            print(f"无效凭据: {ip} - 用户: {username} - 密码: {password}")
        else:
            print(f"发生错误: {str(e)}")


# 创建线程
def worker(ip, usernames, passwords):
    for username in usernames:
        for password in passwords:
            check_credentials(ip, username, password)


if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='弱口令检查工具')
    parser.add_argument('-i', '--ip', required=True, help='IP 列表文件路径')
    parser.add_argument('-u', '--user', required=True, help='用户名文件路径')
    parser.add_argument('-p', '--password', required=True, help='密码文件路径')

    args = parser.parse_args()

    # 加载 IP 列表、用户名和密码文件
    ip_list = load_file(args.ip)
    usernames = load_file(args.user)
    passwords = load_file(args.password)

    threads = []
    for ip in ip_list:
        thread = threading.Thread(target=worker, args=(ip, usernames, passwords))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("所有检查完成。")

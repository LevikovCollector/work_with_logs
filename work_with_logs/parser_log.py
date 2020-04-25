import argparse
import re
import json
import os
import collections

log_lines = []
parser = argparse.ArgumentParser(description='Process access.log', argument_default=None)
parser.add_argument('-f', dest='file',  action='store', help='Path to logfile', default='access.log')
parser.add_argument('-d', dest='dir',  action='store', help='Directory where find log file')
parser.add_argument('-n', dest='file_name',  action='store')
parser.add_argument('-all_logs', dest='all',  action='store_true', default=False)

args = parser.parse_args()


def read_logs(path):
    clients_errors = ['404','401','403','400']
    serv_error = ['500','502','503']
    with open(path) as file:
        request_num = 0
        ip_list = []
        method_list = []
        client_error = []
        server_error = []
        res_d = {}
        for line in file.readlines():
            try:
                ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD)", line)
                code400 = re.search(r"\"\s(404|401|403|400)", line)
                code500 = re.search(r"\"\s(500|502|503)", line)
                url = re.search(r"{}\s(.\w+)+".format(method.group(1)), line)

                if code400 is not None:
                    if code400.group(1) in clients_errors:
                        client_error.append((method.group(1), url.group(), code400.group(1), ip.group()))

                if code500 is not None:
                    if code500.group(1) in serv_error:
                        server_error.append((method.group(1), url.group(), code500.group(1), ip.group()))

                if ip is not None and method is not None:
                    ip_list.append(ip.group())
                    method_list.append(method.group(1))

            except AttributeError:
                pass
            request_num += 1

        most_10_cl_server = []
        for error_srv, num in collections.Counter(server_error).most_common(10):
            most_10_cl_server.append({'server_error': error_srv})
        res_d['srv_error'] = most_10_cl_server

        most_10_cl_error = []
        for error_cl, num in collections.Counter(client_error).most_common(10):
            most_10_cl_error.append({'clients_error': error_cl})
        res_d['cl_error'] = most_10_cl_error

        res_d['method'] = collections.Counter(method_list)
        res_d['all_request_count'] = request_num
        most_active_ip = []
        for ip, num in collections.Counter(ip_list).most_common(10):
            most_active_ip.append({ip: num})

        res_d['ip'] = most_active_ip
        print(json.dumps(res_d))


try:

    if args.dir is not None:
        if args.all:
            file_path = []
            files = os.listdir(args.dir)
            only_log = filter(lambda x:x.endswith('.log'),files)
            for file in only_log:
                file_path.append('{}/{}'.format(args.dir, file))
        else:
            file_path = '{}/{}'.format(args.dir, args.file_name)

    elif args.file is not None:
        file_path = args.file
    else:
        raise Exception('Не указан путь к файлу или директория к логам')

    if type(file_path) is str:
        read_logs(file_path)
    else:
        for path in file_path:
            f_name = path.split('/')[-1]
            print('Открыт файл: ' + f_name)
            read_logs(path)
            print('Закрыт файл: ' + f_name + '\n')

except FileNotFoundError:
    print('Файл или директория не найдены')




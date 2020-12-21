# coding=UTF-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import subprocess
import time

SPLIT_SIZE = 20
TAR_SIZE = 16


# For test KB
# SPLIT_SIZE = 10.0
# TAR_SIZE = 5.0


def getFiles(path, suffix):
    return [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if file.endswith(suffix)]


def getGBFileSize(sizeBytes):
    sizeBytes = float(sizeBytes)
    result = float(abs(sizeBytes))
    gbSize = result / 1024 / 1024 / 1024
    # kbSize = result / 1024
    return format(gbSize, '.2f')
    # return format(kbSize, '.2f')


def writeRecord(info, output):
    timestr = time.strftime("%Y-%m-%d", time.localtime())
    filename = output + '/' + timestr + '_record.txt'
    with open(filename, 'a+', encoding="utf-8") as file_object:
        tar_name = info[0]
        file_name = info[1]
        file_size = info[2]
        file_object.write(tar_name + ',' + file_name + ',' + file_size + "\n")
    file_object.close()


def splitFiles(splitFileList, out_path):
    for file in splitFileList:
        name = file[0]
        size = file[1]
        timestamp = str(round(int(time.time() * 1000)))
        targetName = name.split('/')[-1]
        cmd = 'split -b 16G ' + name + ' ' + out_path + '/' + timestamp + '_' + targetName
        # cmd = 'split -b 10K ' + name + ' ' + out_path + '/' + timestamp + '_' + targetName
        process = subprocess.run(args=cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        writeRecord([targetName, name, size], out_path)
        print(process)


def tarFiles(tarFileList, out_path):
    total = 0
    subList = []
    tarList = []
    for file in tarFileList:
        name = file[0]
        size = float(file[1])
        total = total + size
        if total > TAR_SIZE:  # tar files
            tarList.append(subList)
            total = 0
            subList = []
        else:
            subList.append(file)
    if len(subList) > 0:  # less than 16Gb files
        tarList.append(subList)
    print('==========================TarList Begin==============================')
    print(tarList)
    print('==========================TarList End==============================')

    for tar in tarList:
        timestamp = str(round(int(time.time() * 1000)))
        tar_fname = 'tar_' + timestamp + '.tar'
        cmd = 'tar -cvf ' + out_path + '/' + tar_fname
        for sub in tar:
            fname = sub[0]
            cmd = cmd + ' ' + fname
            writeRecord([tar_fname, fname, sub[1]], out_path)
        process = subprocess.run(args=cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print(process)


def filterFile(fileInfos):
    splitFileList = []
    tarFileList = []
    cpFileList = []
    for file in fileInfos:
        name = file[0]
        size = float(file[1])
        if size >= SPLIT_SIZE:
            splitFileList.append(file)
        elif size < TAR_SIZE:
            tarFileList.append(file)
        elif TAR_SIZE <= size < SPLIT_SIZE:
            cpFileList.append(file)
    print('==========================FilterList Begin==============================')
    print(splitFileList)
    print(tarFileList)
    print(cpFileList)
    print('==========================FilterList End==============================')
    return splitFileList, tarFileList, cpFileList


def cpFiles(cpFileList, out_path):
    for file in cpFileList:
        timestamp = str(round(int(time.time() * 1000)))
        name = file[0]
        size = file[1]
        targetName = name.split('/')[-1]
        cmd = 'cp ' + file[0] + ' ' + out_path + '/' + timestamp + '_' + targetName
        process = subprocess.run(args=cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        writeRecord([targetName, name, size], out_path)
        print(process)


if __name__ == '__main__':
    arg_count = len(sys.argv)
    if arg_count < 3:
        print("Please input source file path & target file path")
    file_path = sys.argv[1]
    out_path = sys.argv[2]
    # fileList = getFiles(file_path, '.go')  # '/home/tiger/develop/lotus'
    fileList = getFiles(file_path, ('.mp4', 'MP4', '.mov', '.MOV'))  # '/home/tiger/develop/lotus'
    fileInfos = []
    for file in fileList:
        stat = os.stat(file)
        fileSize = getGBFileSize(stat.st_size)
        fileInfos.append([file.replace(' ', '\ '), fileSize])
        # print(file, fileSize)
    print('==========================FindFiles Begin==============================')
    print(fileInfos)
    print('==========================FindFiles End==============================')
    splitFileList, tarFileList, cpFileList = filterFile(fileInfos)
    splitFiles(splitFileList, out_path)
    tarFiles(tarFileList, out_path)
    cpFiles(cpFileList, out_path)

import streamlit as st
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import statistics


def convert_to_numeric(df):
    return df.apply(pd.to_numeric, errors='coerce')

figure = plt.figure(figsize=(12,18))
axes = [figure.add_subplot(3, 2, i + 1) for i in range(6)]
# path=r"D:\热波机台实验测试数据备份\0114测试激光器\对比0117QI"
data_l=[]
dataconbain=[]
Row_data=[]
date=[]
def std(nums):
    n = len(nums)
    avg = sum(nums) / n
    return (sum(map(lambda e: (e - avg) * (e - avg), nums)) / n) ** 0.5
#streamlit界面设置
st.title("DM处理")

path = st.text_input("请输入文件路径(省略引号)", "")
process_button = st.button('开始处理')

if process_button:
    if path:
        for root,dirs,files in os.walk(path):
             for file in files:
                 if file.endswith('_RawData.xlsx'):
                     # os.path,join(路径 ，文件名称)组合路径
                     filepath = os.path.join(root, file)
                     # re.finfall(正则,file) 查找所有与正则表达式匹配的子串，并返回一个列表
                     name1=re.findall(r"LP1_(\d+)",file)
                     date1=re.findall(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",file)
                     data1=pd.read_excel(filepath)
                     Ave=data1['TW infinity'].mean()
                     Sigma = std(data1['TW infinity']) / Ave
                     AveProbe=data1['Incident Probe'].mean()
                     AvePump=data1['Incident Pump'].mean()
                     AveCo = data1['TW corrected'].mean()
                     STDCo = std(data1['TW corrected'])
                     TWRaw=data1['TW raw'].mean()
                     ReProbe=data1['Reflected Probe'].mean()
                     RePump=data1['Reflected Pump'].mean()

                     # IncidentProbe=data1['Incident Probe'].mean()
                     data_l.append({'name': name1, 'datetime': date1[0].replace('_',' '),'TWcorrected':AveCo,'TWcorrected_STD':STDCo,'L':data1['TW infinity'][0],'B':data1['TW infinity'][1],'C':data1['TW infinity'][2],'T':data1['TW infinity'][3],'R':data1['TW infinity'][4],'Ave':Ave,'AveProbe':AveProbe,'AvePump':AvePump,'Reflected Probe':ReProbe,'RePump':RePump,'Lraw':data1['TW raw'][0],'Braw':data1['TW raw'][1],'Craw':data1['TW raw'][2],'Traw':data1['TW raw'][3],'Rraw':data1['TW raw'][4],'TWRaw':TWRaw})
                     print(filepath)



                 if file.endswith('_Point_Test.csv'):
                    filepath2 = os.path.join(root, file)
                    data=pd.read_csv(filepath2, low_memory=False)
                    # iloc[行-1，列-1]严格搜素
                    autoshift=data.iloc[16,1]
                    # .dropna(axis=0-行/1-列)删除缺失值
                    extra_data=data.iloc[2:8,1:].dropna(axis=1,how='all')
                    ATF_V=data.iloc[12,1:].dropna().to_frame().T
                    Z=data.iloc[15,1:].dropna().to_frame().T
                    # Z=data.iloc[15,1]
                    # .T 转置
                    extra_data=pd.concat([extra_data,ATF_V,Z],ignore_index=True)

                    spot = 9
                    num_parts = (len(extra_data.columns) + spot - 1) // spot
                    # 分割 DataFrame
                    parts = [extra_data.iloc[:, i * spot: (i + 1) * spot] for i in range(num_parts)]

                    # 将每个部分转换为数值类型g
                    numeric_parts = [convert_to_numeric(part) for part in parts]
                    # # 计算每个部分的行平均值
                    mean_values = [part.mean(axis=1) for part in numeric_parts]
                    extra_data=pd.DataFrame(mean_values).mean(axis=0)

                    Row_data.append({'autoshift':autoshift,
                                     'Z':extra_data[7],
                                     # 'Z':Z,
                                     'Chamber T':extra_data[0],'Stage T':extra_data[1],'Laser T':extra_data[2],'Envir T':extra_data[3],'Object T':extra_data[4],'Up_optic T':extra_data[5],'ATF V':extra_data[6]})

        # 提取 datetime 和 Ave 数据
        datetimes = [entry['datetime'] for entry in data_l]
        aves = [entry['Ave'] for entry in data_l]
        averaw = [entry['TWRaw'] for entry in data_l]
        aveprobe=[entry['AveProbe'] for entry in data_l]
        avepump=[entry['AvePump'] for entry in data_l]
        chamberT=[entry['Chamber T'] for entry in Row_data]
        EnvirT=[entry['Envir T'] for entry in Row_data]
        # Z=[entry['Z'] for entry in Row_data]

        def calculate_sigma_vpp(data_list, label):
            if not data_list:
                print(f"No data available for {label}")
                return None, None

            mean_value = sum(data_list) / len(data_list)
            std_value = statistics.stdev(data_list)
            sigma = std_value / mean_value

            max_value = max(data_list)
            min_value = min(data_list)
            vpp = (max_value - min_value) / mean_value

            print(f"{label} - Sigma: {sigma}, Vpp: {vpp}")
            return sigma, vpp


        # 计算各个列表的 sigma 和 Vpp
        sigma_aves, vpp_aves = calculate_sigma_vpp(aves, 'aves')
        sigma_averaw, vpp_averaw = calculate_sigma_vpp(averaw, 'averaw')
        sigma_aveprobe, vpp_aveprobe = calculate_sigma_vpp(aveprobe, 'aveprobe')
        sigma_avepump, vpp_avepump = calculate_sigma_vpp(avepump, 'avepump')
        sigma_chamberT, vpp_chamberT = calculate_sigma_vpp(chamberT, 'chamberT')
        sigma_EnvirT, vpp_EnvirT = calculate_sigma_vpp(EnvirT, 'EnvirT')
        # sigma_Z, vpp_Z = calculate_sigma_vpp(Z, 'Z')
        # 绘制图表并添加 sigma 和 Vpp 文本
        axes[1].plot(datetimes, aves, marker='.')
        axes[1].set_title('TWinfinity')
        axes[1].set_xlabel('datetime')
        axes[1].set_ylabel('TWinfinity')
        axes[1].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[1].text(0.02, 0.95, f'Sigma: {sigma_aves * 100:.3f}%\nVpp: {vpp_aves * 100:.3f}%', transform=axes[1].transAxes, fontsize=10, verticalalignment='top')



        axes[0].plot(datetimes, averaw, marker='.')
        axes[0].set_title('TWraw')
        axes[0].set_xlabel('datetime')
        axes[0].set_ylabel('TWraw')
        axes[0].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[0].text(0.02, 0.95, f'Sigma: {sigma_averaw * 100:.3f}%\nVpp: {vpp_averaw * 100:.3f}%', transform=axes[0].transAxes, fontsize=10, verticalalignment='top')

        axes[2].plot(datetimes, aveprobe, marker='.')
        axes[2].set_title('IncidentProbe')
        axes[2].set_xlabel('datetime')
        axes[2].set_ylabel('IncidentProbe')
        axes[2].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[2].text(0.02, 0.95, f'Sigma: {sigma_aveprobe * 100:.3f}%\nVpp: {vpp_aveprobe * 100:.3f}%', transform=axes[2].transAxes, fontsize=10, verticalalignment='top')

        axes[3].plot(datetimes, avepump, marker='.')
        axes[3].set_title('IncidentPump')
        axes[3].set_xlabel('datetime')
        axes[3].set_ylabel('IncidentPump')
        axes[3].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[3].text(0.02, 0.95, f'Sigma: {sigma_avepump * 100:.3f}%\nVpp: {vpp_avepump * 100:.3f}%', transform=axes[3].transAxes, fontsize=10, verticalalignment='top')

        axes[4].plot(datetimes, chamberT, marker='.')
        axes[4].set_title('ChamberT')
        axes[4].set_xlabel('datetime')
        axes[4].set_ylabel('ChamberT')
        axes[4].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[4].text(0.02, 0.95, f'Sigma: {sigma_chamberT * 100:.3f}%\nVpp: {vpp_chamberT * 100:.3f}%', transform=axes[4].transAxes, fontsize=10, verticalalignment='top')

        axes[5].plot(datetimes, EnvirT, marker='.')
        axes[5].set_title('EnvirT')
        axes[5].set_xlabel('datetime')
        axes[5].set_ylabel('EnvirT')
        axes[5].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[5].text(0.02, 0.95, f'Sigma: {sigma_EnvirT * 100:.3f}%\nVpp: {vpp_EnvirT * 100:.3f}%', transform=axes[5].transAxes, fontsize=10, verticalalignment='top')


        # 旋转刻度标签
        plt.setp(axes[1].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(axes[0].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(axes[2].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(axes[3].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(axes[4].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(axes[5].get_xticklabels(), rotation=45, ha='right', fontsize=8)
        # plt.setp(axes[6].get_xticklabels(), rotation=45, ha='right', fontsize=8)

        data_l=pd.DataFrame(data_l)
        Row_data=pd.DataFrame(Row_data)
        data_l=pd.concat([data_l,Row_data],axis=1)
        # date_format = "%Y-%m-%d %H-%M-%S"
        # plottime(data_l['datetime'],data_l['L'],date_format,'Signal')
        # data_l.to_excel(path,'DMdata.xlsx')
        # 设置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False

        # 显示图表
        plt.tight_layout()
        # plt.show()
        st.pyplot(figure)
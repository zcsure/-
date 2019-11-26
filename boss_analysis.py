#!/usr/bin/env python
# coding: utf-8


import numpy as np
import re
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pyecharts.charts import Geo
from pyecharts import options as opts
from collections import Counter
df = pd.read_csv('job.csv')
df.columns = ['city','position','salary','company','exp','edu']
# df.info()
zhaopin = df.drop_duplicates(inplace = False)
# zhaopin.shape
# zhaopin.isnull().sum()
zhaopin.exp.fillna('不限经验',inplace=True)
zhaopin['standard'] = np.where(zhaopin.salary.str.contains('/天'),0,1)
salarySplit = zhaopin.salary.str.split('-',expand=True)
zhaopin['lowsalary'],zhaopin['highsalary'] = salarySplit[0],salarySplit[1]
lower = zhaopin.lowsalary.apply(lambda x: re.search('(\d+)', x).group(1)).astype(float)
zhaopin.lowsalary = np.where((zhaopin.standard == 0),lower*21/1000,lower)
higher = zhaopin.highsalary.apply(lambda x:re.search('(\d+).*?',x).group(1)).astype(float)
zhaopin.highsalary = np.where((zhaopin.standard == 0),higher*21/1000,higher)
zhaopin.drop(['salary','standard'],axis=1,inplace=True)

#----------------------------------
#各城市岗位数量
place = zhaopin.city
data = Counter(place).most_common() #计算每一座城市的招聘信息数量，生成一个由元组组成的列表
cityJobCount = (
    Geo()
    .add_schema(maptype="china",itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"))
    .add('',data)
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(is_piecewise=True,max_=30000,split_number=10), #1表示对数值分段，2表示分段的最大值，3表示分段个数
        title_opts=opts.TitleOpts(title="boss直聘各地区职位需求量图"),
    )
)
cityJobCount.render() #生成html文件

#-------------------------------

#-------------------------------
#岗位经验和学历要求图
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']#解决matplotlib中文乱码问题
fig,ax = plt.subplots(1,2,figsize=(30,8)) #一行两列的图表
edu_count = zhaopin.edu.value_counts()
exp_count = zhaopin.exp.value_counts()
explode=(0.1,0,0,0,0,0,0,0,0)
ax[0].pie(edu_count,autopct='%.2f%%',labels=edu_count.index,explode=explode,radius=2,textprops={'fontsize':20,'color':'black'})
ax[0].set_title('岗位学历要求',fontsize=24)
ax[1].barh(exp_count.index,width=exp_count.values,height = bar_width)
ax[1].set_title('岗位经验要求',fontsize=24)

for y,x in enumerate(exp_count.values):
    ax[1].text(x+1000,y-0.1,'%s' %x,ha='center',va='bottom')
# plt.yticks(index + bar_width,exp_count.index)  
#---------------------------

#-----------------------------
#各城市岗位数量和工资水平
zhaopin.lowsalary,zhaopin.highsalary = zhaopin.lowsalary.astype(float),zhaopin.highsalary.astype(float)
salary_city = zhaopin.groupby('city',as_index=False)['lowsalary','highsalary'].mean()#以城市为筛选条件求工资平均
workplace = zhaopin.groupby('city',as_index=False)['position'].count().sort_values('position',ascending=False) #将每个城市的职位数求和放在position这里列
workplace = pd.merge(workplace,salary_city,how='left',on='city') #城市和平均工资列合并

fig,ax = plt.subplots(2,1,figsize = (10,10))
ax[0].bar(workplace.city,workplace.position,width=0.8,alpha=0.8)
ax[1].plot(workplace.city,workplace.highsalary*1000,'--',color='b',alpha=0.9,label='最高工资平均数')
ax[1].plot(workplace.city,workplace.lowsalary*1000,'--',color='r',alpha=0.9,label='最低工资平均数')
for x,y in enumerate(workplace.highsalary*1000):
    ax[1].text(x,y,'%.0f' %y,ha='center',va='bottom') #这里的x，y对应着上面已经画好图的各个点的值,只有设置了x，y才能正确对应上点
for x,y in enumerate(workplace.lowsalary*1000):
    ax[1].text(x,y,'%.0f' %y,ha='center',va='bottom')
for x,y in enumerate(workplace.position):
    ax[0].text(x,y,'%.0f' %y,ha='center',va='bottom')
ax[1].legend() #添加图例，也就是右上角的个框里面的示例，名称根据label来
ax[0].set_title('各城市岗位数量')
ax[1].set_title('各城市薪资水平')
#---------------------------------

#---------------------------------
#北京各个岗位的招聘数量
beijing = zhaopin[zhaopin.city.str.contains('北京')]
beijing['count'] = beijing['city']
beijing.drop(['city'],axis=1,inplace=True)
beijing_jobsalary = beijing.groupby('position'，as_index=False)['lowsalary','highsalary'].mean()
beijing_jobcount = beijing.groupby('position',as_index=False)['count'].count().sort_values('count',ascending=False)
beijing_job = pd.merge(beijing_jobcount,beijing_jobsalary,how='left',on='position')

fig,ax = plt.subplots(2,1,figsize=(150,18))
ax[0].plot(beijing_job.position,beijing_job.lowsalary*1000,'--',color='r',alpha=0.9,label='北京各职位平均最低工资')
ax[0].plot(beijing_job.position,beijing_job.highsalary*1000,'--',color='b',alpha=0.9,label='北京地区各职位平均最高工资')
ax[1].bar(beijing_job.position,beijing_job['count'],width=0.8,alpha=0.8)
for x,y in enumerate(beijing_job.lowsalary*1000):
    ax[0].text(x,y,'%.0f' %y,ha='left',va='bottom')
for x,y in enumerate(beijing_job.highsalary*1000):
    ax[0].text(x,y,'%.0f' %y,ha='right',va='bottom')
for x,y in enumerate(beijing_job['count']):
    ax[1].text(x,y,'%s' %y,ha='center',va='bottom')
ax[0].legend()
ax[0].set_title('北京各岗位薪资水平')
ax[1].set_title('北京各岗位招聘数量')
#=-------------------------------------


#----------------------------------
#工作经验对工资的影响
salary_exp = zhaopin.groupby('exp',as_index=False)['lowsalary','highsalary'].mean()
plt.plot(salary_exp.exp,salary_exp.lowsalary*1000,'--',color='g',alpha=0.9,label='各工作经验对应平均最低工资')
plt.plot(salary_exp.exp,salary_exp.highsalary*1000,'-',color='b',alpha=0.9,label='各工作经验对应平均最高工资')
for x,y in enumerate(salary_exp.lowsalary*1000):
    plt.text(x,y,'%.0f' %y,ha='center',va='bottom')
for x,y in enumerate(salary_exp.highsalary*1000):
    plt.text(x,y,'%.0f' %y,ha='center',va='bottom')
plt.legend()
plt.title('工作经验与薪资关系表')
#--------------------------------

#---------------------------------
#学历对工资影响
flg = plt.figure(figsize=(9,7))
salary_edu = zhaopin.groupby('edu',as_index=False)['lowsalary','highsalary'].mean()
plt.plot(salary_edu.edu,salary_edu.lowsalary*1000,'--',color='g',alpha=0.9,label='各学历对应平均最低工资')
plt.plot(salary_edu.edu,salary_edu.highsalary*1000,'--',color='b',alpha=0.9,label='各学历对应平均最高工资')
for x,y in enumerate(salary_edu.lowsalary*1000):
    plt.text(x,y,'%.0f' %y,ha='right',va='bottom')
for x,y in enumerate(salary_edu.highsalary*1000):
    plt.text(x,y,'%.0f' %y,ha='right',va='bottom')
plt.legend()
plt.title('学历要求与薪资关系表')

#-------------------------------------





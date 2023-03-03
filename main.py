# """
# This is the main script for the streamlit app to visualize the daily standup update records.
# The data is stored in a csv file, and the script will read the data and visualize it.
# The script is written in Python 3.8.5.
# author: Yannan Su
# date: 2023-03-02

# streamlit run /Users/su/DS-projects/phd-standup-updates/main.py
# """

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import streamlit as st

# plt.style.use('ggplot')
# sns.set_style('whitegrid')
sns.set_style('white')
sns.set_palette('Set2')
st.set_page_config(layout="wide")

st.markdown("# Standup Update Records")

# add sidebars for selecting person and month
sidebar_person = st.sidebar
people = ['Yannan', 'Lingyue']
person_selector = sidebar_person.selectbox("Select a Person", people)

sidebar_month = st.sidebar
months = {'all months': '2023-',
          'Jan 2023': '2023-1-', 
          'Feb 2023': '2023-2-', 
          'Mar 2023': '2023-3-', 
          'Apr 2023': '2023-4-', 
          'May 2023': '2023-5-', 
          'Jun 2023': '2023-6-', 
          'Jul 2023': '2023-7-', 
          'Aug 2023': '2023-8-', 
          'Sep 2023': '2023-9-', 
          'Oct 2023': '2023-10-', 
          'Nov 2023': '2023-11-', 
          'Dec 2023': '2023-12-'}
month_selector = sidebar_month.selectbox("Select a Month", months.keys())

st.markdown(f"## {month_selector}")

# add checkboxes for selecting figures
show_fig1 = st.sidebar.checkbox("All in one plot over time")
show_fig2 = st.sidebar.checkbox("Relation between productivity and task time")
show_fig3 = st.sidebar.checkbox("Components of tasks")
show_fig4 = st.sidebar.checkbox("Progress by date")
show_fig5 = st.sidebar.checkbox("Progress by weekday")
show_fig6 = st.sidebar.checkbox("Lingering tasks")
show_fig7 = st.sidebar.checkbox("Word counts by date")
show_fig8 = st.sidebar.checkbox("Word counts by weekday")
show_fig9 = st.sidebar.checkbox("Working hours by date")
show_fig10 = st.sidebar.checkbox("Working hours by weekday")
show_fig11 = st.sidebar.checkbox("Working hours for each task")
show_fig12 = st.sidebar.checkbox("Working hours vs. Planned hours")


# """
# Prepare data
# """

# load data
dat = pd.read_csv(f'Daily-Standup-update-{person_selector}_2023.csv')
if person_selector == 'Lingyue':
    # rename the columns AccomplishState1 (%) to Progress1/%
    dat.rename(columns={'AccomplishState1 (%)': 'Progress1/%'}, inplace=True)
    dat.rename(columns={'AccomplishState2 (%)': 'Progress2/%'}, inplace=True)
    dat.rename(columns={'SpentTime1 (h)': 'SpentTime1/h'}, inplace=True)
    dat.rename(columns={'SpentTime2 (h)': 'SpentTime2/h'}, inplace=True)
    dat.rename(columns={'ExtraTime (h)': 'ExtraTime/h'}, inplace=True)
    dat.rename(columns={'WeekCount': 'WeekID'}, inplace=True)
    dat.rename(columns={'TotalWordCount': 'WordCount'}, inplace=True)
    dat.rename(columns={'TaskType1': 'Type1'}, inplace=True)
    dat.rename(columns={'TaskType2': 'Type2'}, inplace=True)

# select the month
dat = dat[dat['Date'].str.contains(months[month_selector])]
dat["Date"] = pd.to_datetime(dat["Date"], format="%Y-%m-%d").dt.date

# fill the missing values with 0 for all numerical columns
dat = dat.fillna(0)

# """
# All in one plot over time
# """
# plot the total progress of each day
# overlay the total task time spent on each task for each day
# overlay the task time + extra time spent on each task for each day
# overlay the productivity for each day

dat['TotalProgress'] = dat["Progress1/%"] + dat["Progress2/%"]
dat['TotalTaskTime'] = dat["SpentTime1/h"] + dat["SpentTime2/h"]
dat['TotalTime'] = dat["TotalTaskTime"] + dat["ExtraTime/h"]

# normalize the values by dividing (max - min)
TotalProgress= (dat['TotalProgress'] - dat['TotalProgress'].min()) / (dat['TotalProgress'].max() - dat['TotalProgress'].min())
TotalTaskTime = (dat['TotalTaskTime'] - dat['TotalTaskTime'].min()) / (dat['TotalTaskTime'].max() - dat['TotalTaskTime'].min())
TotalTime = (dat['TotalTime'] - dat['TotalTime'].min()) / (dat['TotalTime'].max() - dat['TotalTime'].min())
ProductivityRating = (dat['ProductivityRating (1-5)'] - dat['ProductivityRating (1-5)'].min()) / (dat['ProductivityRating (1-5)'].max() - dat['ProductivityRating (1-5)'].min())
WordCount = (dat['WordCount'] - dat['WordCount'].min()) / (dat['WordCount'].max() - dat['WordCount'].min())

fig1, ax = plt.subplots(figsize=(10, 5))
x_date = np.arange(len(dat['Date']))
ax.plot(x_date, TotalProgress, label='TotalProgress')
ax.plot(x_date, TotalTaskTime, label='TotalTaskTime')
ax.plot(x_date, TotalTime, label='TotalTime')
ax.plot(x_date, ProductivityRating, label='Productivity')
ax.plot(x_date, WordCount, label='WordCount')

# ax.plot(dat['Date'], dat['TotalTime'], label='TotalTime')
# ax.plot(dat['Date'], dat['ProductivityRating (1-5)'], label='Productivity')
# ax.plot(dat['Date'], dat['WordCount'], label='WordCount')
plt.legend()
ax.set_xticks(x_date)
ax.set_xticklabels(dat['Date'], rotation=90)
# plt.title('All in one plot over time (normalized)')
if show_fig1:
    st.markdown("### All in one plot over time (normalized by (max - min))")
    st.pyplot(fig1)

# """
# Regression plot between productivity and total task time
# """
# regression plot between productivity and total task time
fig2, ax = plt.subplots(figsize=(10, 5))
sns.regplot(x=dat['TotalTaskTime'], y=dat['ProductivityRating (1-5)'], data=dat, ax=ax)
# plt.title('Regression plot between productivity and total task time')
if show_fig2:
    st.markdown("### Regression plot between productivity and total task time")
    st.pyplot(fig2)

# """
# Components of tasks
# """
# split the df into twp df: date, task1, task2
dat_task_1 = dat[['WeekID', 'Date', 'Weekday', 
                        'Task1','Manuscript1', 'Type1', 'Progress1/%', 'SpentTime1/h']]

dat_task_2 = dat[['WeekID', 'Date', 'Weekday', 
                        'Task2', 'Manuscript2', 'Type2', 'Progress2/%', 'SpentTime2/h']]

# remove the numbers in the column names of dat_task_1
dat_task_1.columns = ['WeekID', 'Date', 'Weekday', 'Task','Manuscript', 'Type', 'Progress/%', 'SpentTime/h']
dat_task_1['TaskIndex'] = 'Task1'

dat_task_2.columns = ['WeekID', 'Date', 'Weekday', 'Task', 'Manuscript', 'Type', 'Progress/%', 'SpentTime/h']
dat_task_2['TaskIndex'] = 'Task2'
# concat the two df vertically
dat_task = pd.concat([dat_task_1, dat_task_2], axis=0)

dat_task.sort_values(by=['WeekID', 'Date', 'TaskIndex'], inplace=True)


fig3, axes = plt.subplots(figsize=(10, 5), ncols=2)
# pie chart of the Task Type 
dat_task['Type'].value_counts().plot.pie(autopct='%1.1f%%', ax=axes[0])
# pie chart of manuscripts
dat_task['Manuscript'].value_counts().plot.pie(autopct='%1.1f%%',ax=axes[1])
# plt.suptitle('Task Type and Manuscript')
if show_fig3:
    st.markdown("### Task Type and Manuscript")
    st.pyplot(fig3)

# """
# Progress by date
# """
dat_state = dat_task[["Date", "Weekday", "TaskIndex", "Progress/%"]]

# replace nan with 0
dat_state = dat_state.replace(np.nan, 0)

# remove % sign in the column 'Progress/%'
# dat_state['Progress/%'] = dat_state['Progress/%'].str.replace('%', '')

# convert the column 'Progress/%' to float
# dat_state['Progress/%'] = dat_state['Progress/%'].astype(float)

# plot the accomplish state of each day as bars
fig4, ax = plt.subplots(figsize=(10, 5))
dat_state_by_date = dat_state[["Date", "Progress/%"]].groupby("Date").sum().reset_index()
dat_state_by_date[["Date", "Progress/%"]].plot(x="Date", y=["Progress/%"], kind="bar", rot=90, ax=ax, color='olive')
plt.ylabel('Progress/% (%)')
# plot two horizontal lines indicate 100% and 200%
plt.axhline(y=100, color='r', linestyle='-')
plt.axhline(y=200, color='r', linestyle='-')
# plt.title('Progress by date')
if show_fig4:
    st.markdown("### Progress by date")
    st.pyplot(fig4)


# """
# Progress by weekday
# """
# fig5, ax = plt.subplots(figsize=(10, 5))
fig5 = sns.catplot(x="Weekday", y="Progress/%", hue="TaskIndex", kind="bar", data=dat_state, ci=68, height=6, aspect=1.5)
# plt.title('Progress by weekday')
if show_fig5:
    st.markdown("### Progress by weekday")
    st.pyplot(fig5)

# """
# Lingering tasks
# """
if show_fig6:
    st.markdown("### 'Lingering' tasks")
    st.dataframe(dat_task.groupby(['Manuscript', 'Type'])['Task'].value_counts().reset_index(name='count').sort_values(by='count', ascending=False))

# """
# Word counts by date
# """
# bar plot wordcount of each day
fig7, ax = plt.subplots(figsize=(10, 5))
dat_raw_wc = dat[["Date", "WordCount"]].groupby("Date").sum().reset_index().sort_values(by='Date')
dat_raw_wc[["Date", "WordCount"]].plot(x="Date", y=["WordCount"], kind="bar", rot=90, ax=ax)
plt.axhline(y=dat_raw_wc['WordCount'].mean(), color='gray', linestyle='--', label='monthly mean')
plt.axhline(y=dat_raw_wc.query("WordCount!=0")['WordCount'].mean(), color='black', linestyle='--', label='writing days mean')
plt.ylabel('Word Count')
plt.legend()
# plt.title('Word counts by date')
if show_fig7:
    st.markdown("### Word counts by date")
    st.pyplot(fig7)

# """
# Word counts by weekday
# """
# fig8, ax = plt.subplots(figsize=(10, 5))
fig8 = sns.catplot(x="Weekday", y="WordCount", kind="bar", data=dat, ci=95, height=6, aspect=1.5)
# plt.title('Word counts by weekday')
if show_fig8:
    st.markdown("### Word counts by weekday")
    st.pyplot(fig8)

# """
# Working hours by date
# """
dat_extra = dat[['WeekID', 'Date', 'Weekday', "ExtraEvent", "ExtraTime/h"]]

dat_extra.rename(columns={'ExtraTime/h': 'SpentTime/h'}, inplace=True)
dat_extra['TaskIndex'] = 'Extra'
dat_extra['Type'] = 'Extra'
# concat it with the dat
dat_st = pd.concat([dat_task, dat_extra], axis=0)


# plot stacked bar chart of Time of each day, colored by TaskIndex
fig9, ax = plt.subplots(figsize=(10, 5))
dat_time = dat_st[["Date", "TaskIndex", "SpentTime/h"]].groupby(["Date", "TaskIndex"]).sum().reset_index()
dat_time.pivot(index="Date", columns= "TaskIndex", values="SpentTime/h").plot(kind="bar", rot=90, ax=ax, stacked=True)
plt.ylabel('Working Time/h')
plt.axhline(y=dat_time.groupby("Date")["SpentTime/h"].sum().mean(), color='black', linestyle='--', label=' mean')
# plt.title('Working hours by date')
if show_fig9:
    st.markdown("### Working hours by date")
    st.pyplot(fig9)

# """
# Working hours by weekday
# """
# plot stacked bar chart of Time of each day, colored by TaskIndex
fig10, ax = plt.subplots(figsize=(10, 5))
dat_time = dat_st[["Weekday", "TaskIndex", "SpentTime/h"]].groupby(["Weekday", "TaskIndex"]).mean().reset_index()
# dat_time = dat_st[["Weekday", "TaskIndex", "SpentTime/h"]].groupby(["Weekday", "TaskIndex"]).sum().reset_index()
dat_time.pivot(index="Weekday", columns= "TaskIndex", values="SpentTime/h").plot(kind="bar", rot=90, ax=ax, stacked=True)
plt.axhline(y=dat_time.groupby("Weekday")["SpentTime/h"].sum().mean(), color='black', linestyle='--', label=' mean')
plt.ylabel('Working Time/h')
# plt.title('Working hours by weekday')
if show_fig10:
    st.markdown("### Working hours by weekday")
    st.pyplot(fig10)

# """
# Working hours by task
# """
# plot pie chart - time spent on each task type
fig11, axes = plt.subplots(figsize=(10, 5), ncols=2)
dat_st.groupby('Type')['SpentTime/h'].sum().plot.pie(autopct='%1.1f%%', ax=axes[0])
dat_st.groupby('Manuscript')['SpentTime/h'].sum().plot.pie(autopct='%1.1f%%', ax=axes[1])
# plt.suptitle('Working hours by task')
if show_fig11:
    st.markdown("### Working hours by task")
    st.pyplot(fig11)

# """
# Working hours vs. Planed hours by date
# """

if person_selector == 'Lingyue':
    dat_task_1_planned = dat[['WeekID', 'Date', 'Weekday', 
                        'Task1', 'Manuscript1', 'Type1', 'PlannedTime1 (h)']]
    dat_task_2_planned = dat[['WeekID', 'Date', 'Weekday', 
                        'Task2', 'Manuscript2', 'Type2', 'PlannedTime2 (h)']]
    dat_task_1_planned.columns = ['WeekID', 'Date', 'Weekday', 'Task','Manuscript', 'Type', 'PlannedTime/h']
    dat_task_1_planned['TaskIndex'] = 'Task1'
    dat_task_2_planned.columns = ['WeekID', 'Date', 'Weekday', 'Task', 'Manuscript', 'Type', 'PlannedTime/h']
    dat_task_2_planned['TaskIndex'] = 'Task2'
    # concat the two df vertically
    dat_task_planned = pd.concat([dat_task_1_planned, dat_task_2_planned], axis=0)

    # fill nan with 0 in the column 'PlannedTime/h'
    dat_task_planned['PlannedTime/h'] = dat_task_planned['PlannedTime/h'].fillna(0)
    dat_task_planned.sort_values(by=['WeekID', 'Date', 'TaskIndex'], inplace=True)

if show_fig12:
    st.markdown("### Working hours vs. Planned hours")
    if person_selector == 'Yannan':
        st.markdown('#### No record of planed hours.')
    else:
        fig12, ax = plt.subplots(figsize=(10, 5))
        # plot lines for the planed hours in dat_task_planned by date
        dat_time = dat_st[["Date", "TaskIndex", "SpentTime/h"]].groupby(["Date", "TaskIndex"]).sum().reset_index().query("TaskIndex!='Extra'")
        dat_time_pivot = dat_time.pivot(index="Date", columns= "TaskIndex", values="SpentTime/h")
        dat_time_pivot.plot(kind="bar", rot=90, ax=ax, stacked=True, zorder=1)
        dat_task_planned[dat_task_planned['TaskIndex']=='Task1'][['PlannedTime/h']].plot(kind="line", ax=ax, rot=90,
                            color='olive', linestyle='--', label='Task1 planned', zorder=2)
        dat_task_planned.groupby('Date')['PlannedTime/h'].sum().reset_index()['PlannedTime/h'].plot(kind="line", ax=ax, rot=90,
                            color='black', linestyle='--', label='Tasks total planned', zorder=3)
        plt.legend()
        plt.ylabel('Working Time/h')
        st.pyplot(fig12)


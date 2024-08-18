import streamlit as st 
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.express as px

st.set_page_config(layout='wide')
st.title('Laboratory')
col1,col2,col3,col4=st.columns(4)


df=pd.read_excel('adlb.xlsx')

visit_group=['SCREENING 1', 'WEEK 2', 'WEEK 4', 'WEEK 6', 'WEEK 8', 'WEEK 12',
       'WEEK 16', 'WEEK 20', 'WEEK 24', 'WEEK 26']
df=df[~df['VISIT'].str.contains('UNSCHEDULED*')]
df['VISIT']=pd.Categorical(df['VISIT'],categories=visit_group,ordered=True)
df['AVISIT']=df['AVISIT'].str.strip()
df['ABSVAL']=df['AVAL']-df['BASE']
df['PCTVAL']=((df['AVAL']-df['BASE'])/df['BASE'])*100

param={'Hemoglobin (mmol/L)':'HGB', 'Hematocrit':'HCT',
       'Ery. Mean Corpuscular Volume (fL)':'MCV',
       'Ery. Mean Corpuscular Hemoglobin (fmol(Fe))':'MCH',
       'Ery. Mean Corpuscular HGB Concentration (mmol/L)':'MCHC',
       'Leukocytes (GI/L)':'WBC', 'Lymphocytes (GI/L)':'LYM', 'Monocytes (GI/L)':'MONO',
       'Eosinophils (GI/L)':'EOS', 'Basophils (GI/L)':'BASO', 'Platelet (GI/L)':'PLAT',
       'Erythrocytes (TI/L)':'RBC'}


def create_baseline_end(data,visit,param):
    figs={}
    data=data.groupby(by=['TRTA','AVISIT','PARAMCD','LBNRIND'])['USUBJID'].count().reset_index()
    for group in data['TRTA'].unique():
        filtered_data=data[data['TRTA']==group]
        fig=px.pie(filtered_data[(filtered_data['AVISIT']==visit) & (filtered_data['PARAMCD']==param)],
                   values='USUBJID',names='LBNRIND',hole=0.5,
                   title=f'Lab Indicator Variables for {group} Group for {visit}')
        figs[group]=fig
    return figs

def pre_post(data,param):
    figs={}
    data=data.groupby(by=['TRTA','AVISIT','PARAMCD','SEX'])['AVAL'].mean().reset_index()
    for group in data['TRTA'].unique():
        filtered_data=data[data['TRTA']==group]
        fig=px.bar(filtered_data[((filtered_data['AVISIT']=='Baseline') | (filtered_data['AVISIT']=='End of Treatment')) & (filtered_data['PARAMCD']==param)],
                   x='SEX',y='AVAL',color='AVISIT',barmode='group',
                   title=f'Pre-Post Treatment for {group} Group for Parameter {param}')
        figs[group]=fig
    return figs

def param_trend(data,param,actual=True):
    if actual:
        figs={}
        data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['AVAL'].mean().reset_index()
        for group in data['TRTA'].unique():
            filtered_data=data[data['TRTA']==group]
            fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
                   x='VISIT',y='AVAL',color='SEX')
            figs[group]=fig
        return figs
    else:
        figs={}
        data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['AVAL'].mean().reset_index()
        for group in data['TRTA'].unique():
            filtered_data=data[data['TRTA']==group]
            fig=px.line(filtered_data[filtered_data['PARAMCD']==("_"+param)],
                   x='VISIT',y='AVAL',color='SEX')
            figs[group]=fig
        return figs

def pct_abs_val(data,param,abs=True):
    data['ABLFL']=data['ABLFL'].fillna('N')
    data=data[data['ABLFL']=='N']
    if abs:
        figs={}
        data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['ABSVAL'].mean().reset_index()
        data=data[data['VISIT']!='SCREENING 1']
        for group in data['TRTA'].unique():
            filtered_data=data[data['TRTA']==group]
            fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
                   x='VISIT',y='ABSVAL',color='SEX')
            figs[group]=fig
        return figs
    else:
        figs={}
        data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['PCTVAL'].mean().reset_index()
        data=data[data['VISIT']!='SCREENING 1']
        for group in data['TRTA'].unique():
            filtered_data=data[data['TRTA']==group]
            fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
                   x='VISIT',y='PCTVAL',color='SEX')
            figs[group]=fig
        return figs



with col1: 
    parameter_option=st.selectbox('Select a Parameter to View',('Hemoglobin (mmol/L)', 'Hematocrit',
       'Ery. Mean Corpuscular Volume (fL)',
       'Ery. Mean Corpuscular Hemoglobin (fmol(Fe))',
       'Ery. Mean Corpuscular HGB Concentration (mmol/L)',
       'Leukocytes (GI/L)', 'Lymphocytes (GI/L)', 'Monocytes (GI/L)',
       'Eosinophils (GI/L)', 'Basophils (GI/L)', 'Platelet (GI/L)',
       'Erythrocytes (TI/L)'))

with col2:
    visit_options=st.selectbox('Select Visit',('Baseline','End of Treatment'))

with col3:
    treatment_option=st.selectbox('Select Treatment',('Placebo','Xanomeline Low Dose','Xanomeline High Dose'))
    if treatment_option=='Placebo':
        selected_treatment='Placebo'
    elif treatment_option=='Xanomeline Low Dose':
        selected_treatment='Trt A'
    elif treatment_option=='Xanomeline High Dose':
        selected_treatment='Trt B'

donut_plots=create_baseline_end(df,visit_options,param[parameter_option])

with col1:
    st.plotly_chart(donut_plots[selected_treatment],use_container_width=True)

pre_post_plot=pre_post(df,param[parameter_option])

with col2:
    st.plotly_chart(pre_post_plot[selected_treatment],use_container_width=True)

act_trend=param_trend(df,param[parameter_option],True)
rel_trend=param_trend(df,param[parameter_option],False)

with col3: 
    agree=st.checkbox('Relative To Normal')
    if agree: 
        st.plotly_chart(rel_trend[selected_treatment],use_container_width=True)
    else:
        st.plotly_chart(act_trend[selected_treatment],use_container_width=True)

with col4:
    abs_or_pct=st.selectbox('Select Change Type:',('Absolute Change','Percentage Change'))
    if abs_or_pct=='Absolute Change':
        abs=True
    else:
        abs=False

abs_plot=pct_abs_val(df,param[parameter_option],abs)

with col4:
    st.plotly_chart(abs_plot[selected_treatment],use_container_width=True)


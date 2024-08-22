import streamlit as st 
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
st.set_page_config(layout='wide')
st.title('Laboratory')
col1,col2,col3=st.columns(3)


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


# def create_baseline_end(data,visit,param):
#     figs={}
#     data=data.groupby(by=['TRTA','AVISIT','PARAMCD','LBNRIND'])['USUBJID'].count().reset_index()
#     for group in data['TRTA'].unique():
#         filtered_data=data[data['TRTA']==group]
#         fig=px.pie(filtered_data[(filtered_data['AVISIT']==visit) & (filtered_data['PARAMCD']==param)],
#                    values='USUBJID',names='LBNRIND',hole=0.5,
#                    title=f'Lab Indicator Variables for {group} Group for {visit}')
#         figs[group]=fig
#     return figs

def pre_post(data,param):
    data=data.groupby(by=['TRTA','AVISIT','PARAMCD'])['AVAL'].mean().reset_index()
    filtered_data=data
    fig=px.bar(filtered_data[((filtered_data['AVISIT']=='Baseline') | (filtered_data['AVISIT']=='End of Treatment')) & (filtered_data['PARAMCD']==param)],
                   x='TRTA',y='AVAL',color='AVISIT',barmode='group',
                   title=f'Pre-Post Treatment for Treatment Group for Parameter {param}')
    return fig

def param_trend(data,param,actual=True):
    data=data.groupby(by=['TRTA','VISIT','PARAMCD'])['AVAL'].mean().reset_index()
    filtered_data=data
    if actual:
        fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
                   x='VISIT',y='AVAL',color='TRTA')
        return fig
    else:

        fig=px.line(filtered_data[filtered_data['PARAMCD']==("_"+param)],
                   x='VISIT',y='AVAL',color='TRTA')
        return fig

# def pct_abs_val(data,param,abs=True):
#     data['ABLFL']=data['ABLFL'].fillna('N')
#     data=data[data['ABLFL']=='N']
#     if abs:
#         figs={}
#         data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['ABSVAL'].mean().reset_index()
#         data=data[data['VISIT']!='SCREENING 1']
#         for group in data['TRTA'].unique():
#             filtered_data=data[data['TRTA']==group]
#             fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
#                    x='VISIT',y='ABSVAL',color='SEX')
#             figs[group]=fig
#         return figs
#     else:
#         figs={}
#         data=data.groupby(by=['TRTA','SEX','VISIT','PARAMCD'])['PCTVAL'].mean().reset_index()
#         data=data[data['VISIT']!='SCREENING 1']
#         for group in data['TRTA'].unique():
#             filtered_data=data[data['TRTA']==group]
#             fig=px.line(filtered_data[filtered_data['PARAMCD']==param],
#                    x='VISIT',y='PCTVAL',color='SEX')
#             figs[group]=fig
#         return figs

def box_treatment(data,param):
    figs={}
    for group in data['TRTA'].unique():
        filtered_data=data[data['TRTA']==group]
        fig=px.box(filtered_data[ (filtered_data['PARAMCD']==param)],
                   x='VISIT',y='AVAL',hover_data=['AVAL','LBNRIND','USUBJID'],
                   title=f'Distribution of Paramter {param}')
        figs[group]=fig
    return figs

def line_with_range(data,param,abs=True):
    data['ABLFL']=data['ABLFL'].fillna('N')
    data=data[data['ABLFL']=='N']
    figs={}
    if abs:
        data=data.groupby(by=['TRTA','VISIT','PARAMCD'])['ABSVAL'].agg([('ABSVAL','mean'),['ABSSTD','std']]).reset_index()
        data=data[data['VISIT']!='SCREENING 1']
        data['UPPER']=data['ABSVAL']+data['ABSSTD']
        data['LOWER']=data['ABSVAL']-data['ABSSTD']

        for group in data['TRTA'].unique():
            filtered_data=data[(data['TRTA']==group) & (data['PARAMCD']==param)]
            fig=go.Figure([go.Scatter(name='Mean Absolute Change',x=filtered_data['VISIT'],y=filtered_data['ABSVAL'],mode='lines',line=dict(color='rgb(31, 119, 180)'),showlegend=False),
                           go.Scatter(name='Upper limit',x=filtered_data['VISIT'],y=filtered_data['UPPER'],mode='lines',marker=dict(color="#444"),line=dict(width=0),fillcolor='rgba(68, 68, 68, 0.3)',fill='tonexty',showlegend=False),
               go.Scatter(name='Lower limit',x=filtered_data['VISIT'],y=filtered_data['LOWER'],mode='lines',marker=dict(color="#444"),line=dict(width=0),fillcolor='rgba(68, 68, 68, 0.3)',fill='tonexty',showlegend=False)])
            figs[group]=fig
        return figs
    else: 
        data=data.groupby(by=['TRTA','VISIT','PARAMCD'])['PCTVAL'].agg([('PCTVAL','mean'),['PCTSTD','std']]).reset_index()
        data=data[data['VISIT']!='SCREENING 1']
        data['UPPER']=data['PCTVAL']+data['PCTSTD']
        data['LOWER']=data['PCTVAL']-data['PCTSTD']

        for group in data['TRTA'].unique():
            filtered_data=data[(data['TRTA']==group) & (data['PARAMCD']==param)]
            fig=go.Figure([go.Scatter(name='Mean Absolute Change',x=filtered_data['VISIT'],y=filtered_data['PCTVAL'],mode='lines',line=dict(color='rgb(31, 119, 180)'),showlegend=False),
                           go.Scatter(name='Upper limit',x=filtered_data['VISIT'],y=filtered_data['UPPER'],mode='lines',marker=dict(color="#444"),line=dict(width=0),fillcolor='rgba(68, 68, 68, 0.3)',fill='tonexty',showlegend=False),
               go.Scatter(name='Lower limit',x=filtered_data['VISIT'],y=filtered_data['LOWER'],mode='lines',marker=dict(color="#444"),line=dict(width=0),fillcolor='rgba(68, 68, 68, 0.3)',fill='tonexty',showlegend=False)])
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
    treatment_option=st.selectbox('Select Treatment',('Placebo','Xanomeline Low Dose','Xanomeline High Dose'))
    if treatment_option=='Placebo':
        selected_treatment='Placebo'
    elif treatment_option=='Xanomeline Low Dose':
        selected_treatment='Trt A'
    elif treatment_option=='Xanomeline High Dose':
        selected_treatment='Trt B'



# with col1:
#     visit_options=st.toggle('View At End Of Treatment')
#     if visit_options:
#         donut_plots=create_baseline_end(df,'End of Treatment',param[parameter_option])
#     else:
#         donut_plots=create_baseline_end(df,'Baseline',param[parameter_option])
#     st.plotly_chart(donut_plots[selected_treatment],use_container_width=True)

pre_post_plot=pre_post(df,param[parameter_option])

with col1:
    st.plotly_chart(pre_post_plot,use_container_width=True)

act_trend=param_trend(df,param[parameter_option],True)
rel_trend=param_trend(df,param[parameter_option],False)

with col2: 
    agree=st.toggle('Relative To Normal')
    if agree: 
        st.plotly_chart(rel_trend,use_container_width=True)
    else:
        st.plotly_chart(act_trend,use_container_width=True)

with col3:
    abs_or_pct=st.selectbox('Select Change Type:',('Absolute Change','Percentage Change'))
    if abs_or_pct=='Absolute Change':
        abs=True
    else:
        abs=False

abs_plot=line_with_range(df,param[parameter_option],abs)

with col3:
    st.plotly_chart(abs_plot[selected_treatment],use_container_width=True)

box_plot=box_treatment(df,param[parameter_option])

with col1: 
    st.plotly_chart(box_plot[selected_treatment],use_container_width=True)


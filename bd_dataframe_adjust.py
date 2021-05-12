import pandas as pd

#select appropriate columns from perf csv.
perf_df = pd.read_csv("D:/glowing-waffle/test/perf.csv",usecols=['WA NUM','UWI','PERF STAGE NUM','CHARGE TYPE','CHARGE SIZE (g)','SHOTS PER METER','DEGREE OF PHASING','PERF COMMENTS'])


#function for applying Frac Type based on the perf data; rudimentary, but should do the job. Two options: Frac Sleeve or Plug and Perf.
def frac_type(row):
    if pd.isna(row['CHARGE TYPE']) == True and pd.isna(['CHARGE SIZE(g)']) == True and pd.isna(row['SHOTS PER METER']) == True and pd.isna(['DEGREE OF PHASING']) == True:
        return 'Frac Sleeve'
    if row['PERF COMMENTS'] == "AbrasiveJet" or row['PERF COMMENTS'] == 'Burst Disc' or row['PERF COMMENTS'] =='Toe Port' or row['PERF COMMENTS']=='Cemented Sleeve':
        return 'Frac Sleeve'
    return 'Plug and Perf'

#apply the function to each row in the dataframe.
perf_df['FRAC TYPE'] = perf_df.apply (lambda row: frac_type(row),axis=1)
df4 = perf_df['FRAC TYPE'].groupby(perf_df['WA NUM']).agg({'count','max'})
df4 = df4.reset_index().drop(['count'], axis=1)
df4 = df4.rename(columns={'max':'Frac Type'})
#perf_group_df = perf_df.groupby('WA NUM')
#df3 = pd.DataFrame()
#df3['Frac Type'] = perf_group_df.apply(lambda x: x['FRAC TYPE'].value_counts().idxmax())

#print(df3.mode())
#selecting appropriate columns from Hydro frac csv, and key computations
hf_df = pd.read_csv("D:/glowing-waffle/test/hydraulic_fracture.csv",usecols= ['WA NUM','UWI','COMPLTN TOP DEPTH (m)','COMPLTN BASE DEPTH (m)','FRAC STAGE NUM','VISCOSITY GEL TYPE','ENERGIZER','ENERGIZER TYPE',
                                                                               'AVG TREATING PRESSURE (MPa)','FRAC GRADIENT (KPa/m)','TOTAL FLUID PUMPED (m3)','TOTAL CO2 PUMPED (m3)','TOTAL N2 PUMPED (scm)',
                                                                               'TOTAL CH4 PUMPED (e3m3)','PROPPANT TYPE1','PROPPANT TYPE1 PLACED (t)','PROPPANT TYPE2','PROPPANT TYPE2 PLACED (t)',
                                                                               'PROPPANT TYPE3','PROPPANT TYPE3 PLACED (t)','PROPPANT TYPE4','PROPPANT TYPE4 PLACED (t)'])

#fill NaN values and sum the Proppant totals; prepping for Tonnage/m. Changing the name of the Visc Gel Type to Fluid System for clarity.
hf_df['PROPPANT TYPE1 PLACED (t)'] = hf_df['PROPPANT TYPE1 PLACED (t)'].fillna(0)
hf_df['PROPPANT TYPE2 PLACED (t)'] = hf_df['PROPPANT TYPE2 PLACED (t)'].fillna(0)
hf_df['PROPPANT TYPE3 PLACED (t)'] = hf_df['PROPPANT TYPE3 PLACED (t)'].fillna(0)
hf_df['PROPPANT TYPE4 PLACED (t)'] = hf_df['PROPPANT TYPE4 PLACED (t)'].fillna(0)
hf_df['Proppant Total'] = hf_df['PROPPANT TYPE1 PLACED (t)'] + hf_df['PROPPANT TYPE2 PLACED (t)'] + hf_df['PROPPANT TYPE3 PLACED (t)'] + hf_df['PROPPANT TYPE4 PLACED (t)']
hf_df.rename(columns={'VISCOSITY GEL TYPE':'Fluid System'}, inplace = True)

#grouping by WA NUM to sum and adjust key values (as the document is set up per stage;
group = hf_df.groupby('WA NUM')
df2 = pd.DataFrame()
df2['Proppant Total Sum'] = group.apply(lambda x: sum(x['Proppant Total']))
df2['Lateral Length'] = group.apply(lambda x:max(x['COMPLTN BASE DEPTH (m)']) - min(x['COMPLTN TOP DEPTH (m)']))
df2['Average Treating Pressure'] = group.apply(lambda x: x['AVG TREATING PRESSURE (MPa)'].mean())
df2['FRAC GRADIENT (KPa/m)'] = group.apply(lambda x: x['FRAC GRADIENT (KPa/m)'].mean())
df2['Tonnage per m'] = df2['Proppant Total Sum'] / df2['Lateral Length']
df2['Tonnage per m'] = df2['Tonnage per m'] .round(2)
df2['Energizer'] =group.apply(lambda x: x['ENERGIZER'].value_counts().index.tolist()[0])
df2['Energizer Type'] = group.apply(lambda x: x['ENERGIZER TYPE'].value_counts().index.tolist()[0])
df2['Total CO2 Pumped (m3)'] =group.apply(lambda x: sum(x['TOTAL CO2 PUMPED (m3)']))
df2['Total N2 Pumped (scm)'] = group.apply(lambda x: sum(x['TOTAL N2 PUMPED (scm)']))
df2['Total CH4 Pumped (e3m3)'] = group.apply(lambda x: sum(x[ 'TOTAL CH4 PUMPED (e3m3)']))
df2 = df2.reset_index()
df2 = df2.drop(['Proppant Total Sum','Lateral Length'],axis = 1)

df = pd.merge(df4, df2, on = 'WA NUM')
df[['Total CO2 Pumped (m3)','Total N2 Pumped (scm)','Total CH4 Pumped (e3m3)']] = df[['Total CO2 Pumped (m3)','Total N2 Pumped (scm)','Total CH4 Pumped (e3m3)']].fillna(value = 0, inplace = True)
print(df)
#df.reset_index()
#print(df.head(5))



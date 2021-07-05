import pandas as pd
import numpy as np 
import xlsxwriter as excel
import re

opp = input("Opponent: ")
team = input("Enter scouting team: ")
data = pd.read_csv(r'/Users/HerschelGupta/Documents/FootballAnalytics/RawData/' + team + '_base_Cuse.csv')
excel_name = opp + 'Analytics.xlsx'
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
finish = False
count = 0

data['pff_RUNPASS'] = data['pff_RUNPASS'].replace(['R','P'],['Run','Pass'])
writer = pd.ExcelWriter(r'/Users/HerschelGupta/Documents/FootballAnalytics/AnalyzedData/' + excel_name, engine='xlsxwriter')
format = writer.book.add_format({'num_format': '0.0%'})
FLSO = writer.book.add_format({'fg_color': '006747','font_color': 'white'}) 
TXUN = writer.book.add_format({'fg_color': 'bf5700','font_color': 'white'})
usf = writer.book.add_format({'font_color': '006747','font_size':24}) 
texas = writer.book.add_format({'font_color': 'bf5700','font_size':24})
largecenter = writer.book.add_format({'align': 'center','valign': 'vcenter','text_wrap': True,'font_size':24})
bold = writer.book.add_format({'align': 'center','bold': True})
center = writer.book.add_format({'align': 'center','valign': 'vcenter','text_wrap': True})
writing = writer.book.add_format({'align': 'left','valign': 'top','text_wrap': True})
red = format1 = writer.book.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006'})
orange = format1 = writer.book.add_format({'bg_color': '#FFFF66','font_color': '#FFA500'})
green = format1 = writer.book.add_format({'bg_color': '#C6EFCE','font_color': '#006100'})



def colorhead(t1,t2,row,col,length,worksheet,final,min,max,*colnames):
    if (team == t1):
        for col_num, value in enumerate(colnames):
            worksheet.write(row, col_num + (count*(length+1)) + col, value, FLSO)
    elif (team == t2):
        for col_num, value in enumerate(colnames):
            worksheet.write(row, col_num + (count*(length+1)) + col, value, TXUN)
    col_f = col_num + (count*(length+1))
    worksheet.conditional_format(row+1,col_f+col,row+1+len(final),col_f+col, {'type': 'cell',
                                            'criteria': '>',
                                            'value': max,
                                            'format': red,
                                            })
    worksheet.conditional_format(row+1,col_f+col,row+1+len(final),col_f+col, {'type': 'cell',
                                            'criteria': 'between',
                                            'minimum': min,
                                            'maximum': max,
                                            'format': orange,
                                            })
    # worksheet.conditional_format(row+1,col_f,row+1+len(final),col_f, {'type': 'cell',
    #                                         'criteria': 'between',
    #                                         'minimum': 0,
    #                                         'maximum': min,
    #                                         'format': green,
    #                                         })

    
            
def FieldBdry(count):
    # PASS BREAKDOWN
    p1 = (data['pff_RUNPASS'] == 'Pass')
    p2 = (data['pff_PASSDIRECTION'] != 'X') 
    p3 = (data['pff_HASH'] != 'C')
    p_data = data[p1 & p2 & p3]
    data['Fld_Bdry_p'] = (p_data['pff_HASH'] == p_data['pff_PASSDIRECTION'])
    data['Fld_Bdry_p'] = data['Fld_Bdry_p'].replace([1,0,np.nan],['Pass_Boundary','Pass_Field','']) 
    
    # RUN BREAKDOWN
    r1 = (data['pff_RUNPASS'] == 'Run') 
    r2 = (data['pff_HASH'] != 'C')
    r_data = data[r1 & r2]
    left = r_data.isin({'pff_POAINTENDED':['LT','LE','ML','LG','JET SWEEP LEFT','END AROUND LEFT']})
    right = r_data.isin({'pff_POAINTENDED':['RT','RE','MR','RG','JET SWEEP RIGHT','END AROUND RIGHT']})
    data['Fld_Bdry_r'] = ((left['pff_POAINTENDED']) & (r_data['pff_HASH'] == 'L')) | ((right['pff_POAINTENDED']) & (r_data["pff_HASH"] == 'R'))
    data['Fld_Bdry_r'] = data['Fld_Bdry_r'].replace([1,0,np.nan],['Run_Boundary', 'Run_Field','']) 


    data['Fld_Bdry'] = data['Fld_Bdry_p'] + data['Fld_Bdry_r'] 
    imp = ['pff_OFFPERSONNELBASIC','pff_RUNPASS','Fld_Bdry']
    impdata = data[(r1 & r2) | (p1 & p2 & p3)]
    impdata = impdata[imp]
    impdata.dropna()
    
    
    sorted = (impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS','Fld_Bdry']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size())
    sorted_ = (impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size())
    sorted.to_excel(writer, sheet_name='Fld_Bdry',startrow = 0,startcol = count*5)
    sorted_.to_excel(writer, sheet_name='Fld_Bdry',startrow = 25,startcol = (count*5))
    ws = writer.sheets['Fld_Bdry']
    # Percentage out of certain play types
    colorhead('FLSO','TXUN',0,0,4,ws,sorted,.5,.65,'Personnel','R/P','Fld/Bdry','Percentage')
    ws.set_column(3+(count*5),3+(count*5), 10, format)
    # # Percentage out of all plays 
    colorhead('FLSO','TXUN',25,0,4,ws,sorted,.5,.65,'Personnel','R/P','Percentage') 
    ws.set_column(2+(count*5),2+(count*5), 20, format)
    

def targeted(count):
    data['TARGET'] = data['pff_PASSRECEIVERTARGET'] + ' - ' + data['pff_PASSRECEIVERPOSITIONTARGET']
    imp = ['pff_OFFTEAM','pff_OFFPERSONNELBASIC','TARGET','pff_PASSRECEIVERTARGET','pff_PASSRECEIVERPOSITIONTARGET','Fld_Bdry_p']
    data['Fld_Bdry_p'] = data['Fld_Bdry_p'].replace([1,0,''],['Pass_Boundary','Pass_Field','Indeterminate'])
    b1 = (data['pff_RUNPASS'] == 'Pass')
    impdata = data[b1]
    impdata = impdata[imp]
    impdata = impdata.dropna()
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','TARGET','Fld_Bdry_p']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Detailed_Targeted',startrow = 0,startcol = count*5)
    worksheet = writer.sheets['Detailed_Targeted']
    worksheet.set_column((count*5),(count*5), 12, None)
    worksheet.set_column(1+(count*5),1+(count*5), 20, None)
    worksheet.set_column(2+(count*5),2+(count*5), 20, None)
    worksheet.set_column(3+(count*5),3+(count*5), 10, format)
    colorhead('FLSO','TXUN',0,0,4,worksheet,sorted,.2,.3,'Personnel','Target','Fld/Bdry','Percentage')
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','TARGET']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Player_Pos_Targeted',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Player_Pos_Targeted']
    worksheet.set_column((count*4),(count*4), 12, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.2,.3,'Personnel','Target','Percentage')
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_PASSRECEIVERTARGET']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Player_Targeted',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Player_Targeted']
    worksheet.set_column((count*4),(count*4), 12, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.2,.3,'Personnel','Player','Percentage')
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_PASSRECEIVERPOSITIONTARGET']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Pos_Targeted',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Pos_Targeted']
    worksheet.set_column((count*4),(count*4), 12, None)
    worksheet.set_column(1+(count*4),1+(count*4), 15, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.2,.3,'Personnel','Position','Percentage')

def runbreakdown(count):
    imp = ['pff_RUNCONCEPTPRIMARY','pff_OFFPERSONNELBASIC','pff_RUNPASSOPTION','pff_RBALIGNMENT']
    b1 = (data['pff_RUNPASS'] == 'Run') & (data['pff_RUNCONCEPTPRIMARY'] != 'UNDEFINED')
    impdata = data[b1]
    impdata = impdata[imp]
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNCONCEPTPRIMARY']).size()/data.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Run_Breakdown',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Run_Breakdown']
    worksheet.set_column((count*4),(count*4), 15, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.5,.65,'Personnel','Run Concept','Percentage')
    rpo = data['pff_RUNPASSOPTION'].sum()/len(data)
    worksheet.write(len(sorted)+2,2+(count*4),rpo,format)
    worksheet.write(len(sorted)+2,1+(count*4),'RPO %')
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNCONCEPTPRIMARY']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Run_Breakdown',startrow = 40,startcol = count*4)
    colorhead('FLSO','TXUN',40,0,3,worksheet,sorted,.5,.65,'Personnel','Run Concept','Percentage')

def earlydowns(count):
    imp = ['pff_RUNPASS','pff_OFFPERSONNELBASIC','pff_DOWN']
    b1 = (data['pff_DOWN'] == 1) | (data['pff_DOWN'] == 2)
    impdata = data[b1]
    impdata = impdata[imp]
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Early_Downs',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Early_Downs']
    worksheet.set_column((count*4),(count*4), 15, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.5,.65,'Personnel','R/P','Percentage')  

def thirddown(count):
    imp = ['pff_RUNPASS','pff_OFFPERSONNELBASIC','pff_DOWN','pff_DISTANCE']
    b1 = data['pff_DOWN'] == 3
    impdata = data[b1]
    impdata = impdata[imp]
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Third_Down',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Third_Down']
    worksheet.set_column((count*4),(count*4), 15, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.5,.65,'Personnel','R/P','Percentage')
    # short = impdata['pff_DISTANCE'] <= 3
    # middle = (3 < impdata['pff_DISTANCE']) & (impdata['pff_DISTANCE'] <= 7)
    # long = 7 < impdata['pff_DISTANCE'] 
    # s_data = impdata[short]
    # sorted = s_data.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/s_data.groupby(['pff_OFFPERSONNELBASIC']).size()
    # print(sorted)
    # m_data = impdata[middle]
    # sorted = m_data.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/m_data.groupby(['pff_OFFPERSONNELBASIC']).size()
    # print(sorted)
    # l_data = impdata[long]
    # sorted = l_data.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/l_data.groupby(['pff_OFFPERSONNELBASIC']).size()
    # print(sorted)

def redzone(count):
    # redzone plays
    redzonedata = pd.read_csv(r'/Users/HerschelGupta/Documents/FootballAnalytics/RawData/' + team + '_redzone_Cuse.csv')
    redzonedata['pff_RUNPASS'] = redzonedata['pff_RUNPASS'].replace(['R','P'],['Run','Pass'])
    redzonedata['TARGET'] = redzonedata['pff_PASSRECEIVERTARGET'] + ' - ' + redzonedata['pff_PASSRECEIVERPOSITIONTARGET']
    imp = ['pff_RUNPASS','pff_OFFPERSONNELBASIC','pff_DOWN']
    impdata = redzonedata[imp]
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RUNPASS']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Redzone',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Redzone']
    worksheet.set_column((count*4),(count*4), 15, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.5,.65,'Personnel','R/P','Percentage')

    # redzone targets
    b1 = (redzonedata['pff_RUNPASS'] == 'Pass')
    imp = ['pff_OFFTEAM','pff_OFFPERSONNELBASIC','TARGET','pff_PASSRECEIVERTARGET','pff_PASSRECEIVERPOSITIONTARGET']
    impdata = redzonedata[b1][imp].dropna()
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_PASSRECEIVERTARGET']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    # print(sorted)
    sorted.to_excel(writer, sheet_name='Redzone_Targets',startrow = 0,startcol = count*4)
    worksheet = writer.sheets['Redzone_Targets']
    worksheet.set_column((count*4),(count*4), 12, None)
    worksheet.set_column(1+(count*4),1+(count*4), 20, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',0,0,3,worksheet,sorted,.2,.3,'Personnel','Player','Percentage')
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_PASSRECEIVERPOSITIONTARGET']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC']).size()
    sorted.to_excel(writer, sheet_name='Redzone_Targets',startrow = 30,startcol = count*4)
    worksheet = writer.sheets['Redzone_Targets']
    worksheet.set_column((count*4),(count*4), 12, None)
    worksheet.set_column(1+(count*4),1+(count*4), 15, None)
    worksheet.set_column(2+(count*4),2+(count*4), 10, format)
    colorhead('FLSO','TXUN',30,0,3,worksheet,sorted,.2,.3,'Personnel','Position','Percentage')


# how rb alignment tells about protection and/or play calls
def rbalignment():
    # protection analysis
    imp =['pff_OFFPERSONNELBASIC','pff_PASSBLOCKING','pff_RBALIGNMENT','pff_RBDEPTH','pff_RUNPASS']
    b1 = (data['pff_RUNPASS'] == 'Pass')
    b2 = data['pff_RBALIGNMENT'] != 'EMPTY'
    impdata = data[b1 & b2]
    impdata = impdata[imp]
    hb = impdata['pff_PASSBLOCKING'].str.contains('(HB)',regex = False)
    hb_l = impdata['pff_PASSBLOCKING'].str.contains('(HB-L)',regex = False)
    hb_r = impdata['pff_PASSBLOCKING'].str.contains('(HB-R)',regex = False)
    fb_l = impdata['pff_PASSBLOCKING'].str.contains('(FB-L)',regex = False)
    fb_r = impdata['pff_PASSBLOCKING'].str.contains('(FB-R)',regex = False)
    te_l = impdata['pff_PASSBLOCKING'].str.contains('(TE-L)',regex = False)
    te_r = impdata['pff_PASSBLOCKING'].str.contains('(TE-R)',regex = False)
    impdata['Blocking_Scheme'] =impdata['pff_PASSBLOCKING'].str[0] + ': ' + hb.replace([1,0],['HB ','']) + hb_l.replace([1,0],['HB-L ','']) + hb_r.replace([1,0],['HB-R ','']) + fb_l.replace([1,0],['FB-L ','']) + fb_r.replace([1,0],['FB-R ','']) + te_l.replace([1,0],['TE-L ','']) + te_r.replace([1,0],['TE-R ',''])
    impdata['Blocking_Scheme'] = impdata['Blocking_Scheme'].replace({'Blocked':'No Extra Blockers'})
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RBALIGNMENT','Blocking_Scheme']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC','pff_RBALIGNMENT']).size()
    sorted.to_excel(writer, sheet_name='RB_Alignment - Blocking',startrow = 0,startcol = count*6)
    worksheet = writer.sheets['RB_Alignment - Blocking']
    worksheet.set_column((count*6),(count*6), 10, None)
    worksheet.set_column(1+(count*6),1+(count*6), 15, None)
    worksheet.set_column(2+(count*6),2+(count*6), 20, None)
    worksheet.set_column(3+(count*6),3+(count*6), 10, format)
    colorhead('FLSO','TXUN',0,0,5,worksheet,sorted,.5,.65,'Personnel','RB Alignment','Blockers','Percentage')

    # play analysis
    sorted = data.groupby(['pff_OFFPERSONNELBASIC','pff_RBALIGNMENT','pff_RUNPASS']).size()/data.groupby(['pff_OFFPERSONNELBASIC','pff_RBALIGNMENT']).size()
    # print(sorted)
    sorted.to_excel(writer, sheet_name='RB_Alignment - Plays',startrow = 0,startcol = count*5)
    worksheet = writer.sheets['RB_Alignment - Plays']
    worksheet.set_column((count*5),(count*5), 10, None)
    worksheet.set_column(1+(count*5),1+(count*5), 15, None)
    worksheet.set_column(2+(count*5),2+(count*5), 10, None)
    worksheet.set_column(3+(count*5),3+(count*5), 10, format)
    colorhead('FLSO','TXUN',0,0,4,worksheet,sorted,.5,.65,'Personnel','RB Alignment','R/P','Percentage')

# how te alignment tells about protection and/or play calls
def tealignment():
    # protection analysis
    imp =['pff_OFFPERSONNELBASIC','pff_PASSBLOCKING','newTEALIGNMENT']
    odd_1 = data['pff_OFFODDITIES'].str.split(';').str[0]
    odd_2 = data['pff_OFFODDITIES'].str.split(';').str[1]
    te_1 = (odd_1.str.split('>').str[0] == 'TE')
    te_2 = (odd_2.str.split('>').str[0] == ' TE')
    odd_1 = odd_1[te_1].str.split('>').str[1]
    odd_2 = odd_2[te_2].str.split('>').str[1]
    data['newTEALIGNMENT'] = data['pff_TEALIGNMENT'].replace([np.nan],['']) + ' ' + te_1.replace([1,0],[odd_1[te_1],'']) + ' ' + te_2.replace([1,0],[odd_2[te_2],''])
    data['newTEALIGNMENT'] = data['newTEALIGNMENT'].str.strip()
    b1 = (data['newTEALIGNMENT'] != '') & (data['pff_RUNPASS'] == 'Pass')
    impdata = data[b1][imp]
    # print(impdata)
    hb = impdata['pff_PASSBLOCKING'].str.contains('(HB)',regex = False)
    hb_l = impdata['pff_PASSBLOCKING'].str.contains('(HB-L)',regex = False)
    hb_r = impdata['pff_PASSBLOCKING'].str.contains('(HB-R)',regex = False)
    fb_l = impdata['pff_PASSBLOCKING'].str.contains('(FB-L)',regex = False)
    fb_r = impdata['pff_PASSBLOCKING'].str.contains('(FB-R)',regex = False)
    te_l = impdata['pff_PASSBLOCKING'].str.contains('(TE-L)',regex = False)
    te_r = impdata['pff_PASSBLOCKING'].str.contains('(TE-R)',regex = False)
    impdata['Blocking_Scheme'] =impdata['pff_PASSBLOCKING'].str[0] + ': ' + hb.replace([1,0],['HB ','']) + hb_l.replace([1,0],['HB-L ','']) + hb_r.replace([1,0],['HB-R ','']) + fb_l.replace([1,0],['FB-L ','']) + fb_r.replace([1,0],['FB-R ','']) + te_l.replace([1,0],['TE-L ','']) + te_r.replace([1,0],['TE-R ',''])
    impdata['Blocking_Scheme'] = impdata['Blocking_Scheme'].replace({'5: Blocked':'None'})
    sorted = impdata.groupby(['pff_OFFPERSONNELBASIC','newTEALIGNMENT','Blocking_Scheme']).size()/impdata.groupby(['pff_OFFPERSONNELBASIC','newTEALIGNMENT']).size()
    # print(sorted)
    sorted.to_excel(writer, sheet_name='TE Alignment - Blocking',startrow = 0,startcol = count*6)
    worksheet = writer.sheets['TE Alignment - Blocking']
    worksheet.set_column((count*6),(count*6), 10, None)
    worksheet.set_column(1+(count*6),1+(count*6), 12, None)
    worksheet.set_column(2+(count*6),2+(count*6), 20, None)
    worksheet.set_column(3+(count*6),3+(count*6), 10, format)
    colorhead('FLSO','TXUN',0,0,5,worksheet,sorted,.5,.65,'Personnel','TE Alignment','Blockers','Percentage')

    # play analysis
    b1 = (data['newTEALIGNMENT'] != '')
    sorted = data[b1].groupby(['pff_OFFPERSONNELBASIC','newTEALIGNMENT','pff_RUNPASS']).size()/data.groupby(['pff_OFFPERSONNELBASIC','newTEALIGNMENT']).size()
    # print(sorted)
    sorted.to_excel(writer, sheet_name='TE Alignment - Plays',startrow = 0,startcol = count*5)
    worksheet = writer.sheets['TE Alignment - Plays']
    worksheet.set_column((count*5),(count*5), 10, None)
    worksheet.set_column(1+(count*5),1+(count*5), 12, None)
    worksheet.set_column(2+(count*5),2+(count*5), 10, None)
    worksheet.set_column(3+(count*5),3+(count*5), 10, format)
    colorhead('FLSO','TXUN',0,0,4,worksheet,sorted,.5,.65,'Personnel','TE Alignment','R/P','Percentage')


def descriptions():
    ws = writer.sheets['Fld_Bdry']
    ws.merge_range(3,10,3,14,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    ws.merge_range(6,10,10,14,'Percentage of run and pass plays, separated by personnel groupings, that go to the field or boundary, out of respective play type from that personnel group.',center)
    ws.merge_range(12,10,17,14,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    ws.merge_range(25,10,29,14,'Percentage of run and pass plays, separated by personnel groupings, out of all possible plays from that personnel group.',center)
    worksheet = writer.sheets['Detailed_Targeted']
    worksheet.merge_range(3,10,3,14,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,10,10,14,'Percentage of targets, separated by personnel, player, starting position, and final location of field or boundary, out of all passing plays in that personnel group.',center)
    worksheet.merge_range(12,10,17,14,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Player_Pos_Targeted']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Percentage of targets, separated by personnel, player, and starting position, out of all passing plays in that personnel group.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Player_Targeted']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Percentage of targets, separated by personnel and player, out of all passing plays in that personnel group.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Pos_Targeted']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Percentage of targets, separated by personnel and starting position, out of all passing plays in that personnel group.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Run_Breakdown']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Percentage of run concepts, separated by personnel group, out of all possible plays from that personnel group.',center)
    worksheet.merge_range(45,8,49,12,'Percentage of run concepts, separated by personnel group, out of all run plays from that personnel group.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['RB_Alignment - Blocking']
    worksheet.merge_range(3,12,3,16,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,12,10,16,'Percentage of extra blockers, separated by personnel group and backfield alignment, out of all possible pass plays from that pairing of alignment and personnel group.',center)
    worksheet.merge_range(12,12,17,16,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['RB_Alignment - Plays']
    worksheet.merge_range(3,10,3,14,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,10,10,14,'Percentage of run and pass plays, separated by personnel group and backfield alignment, out of all possible plays from that pairing of alignment and personnel group.',center)
    worksheet.merge_range(12,10,17,14,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['TE Alignment - Blocking']
    worksheet.merge_range(3,12,3,16,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,12,10,16,'Percentage of extra blockers, separated by personnel group and TE alignment, out of all possible pass plays from that pairing of alignment and personnel group.',center)
    worksheet.merge_range(12,12,17,16,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['TE Alignment - Plays']
    worksheet.merge_range(3,10,3,14,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,10,10,14,'Percentage of run or pass plays, separated by personnel group and TE alignment, out of all possible plays from that pairing of alignment and personnel group.',center)
    worksheet.merge_range(12,10,17,14,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Early_Downs']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Run and Pass percentages based on personnel group on early downs (1st and 2nd) of all distances.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Third_Down']
    worksheet.merge_range(3,8,3,12,'ALL FROM BASE PLAYS (NO 2M,4M,RZ,GT)',bold)
    worksheet.merge_range(6,8,10,12,'Run and Pass percentages based on personnel group on third downs of all distances.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Redzone']
    worksheet.merge_range(3,8,3,12,'ALL FROM REDZONE PLAYS',bold)
    worksheet.merge_range(6,8,10,12,'Run and Pass percentages based on personnel group in the red zone for all downs.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)
    worksheet = writer.sheets['Redzone_Targets']
    worksheet.merge_range(3,8,3,12,'ALL FROM REDZONE PLAYS',bold)
    worksheet.merge_range(6,8,10,12,'Percentage of targets, separated by personnel and player, out of all redzone passing plays in that personnel group.',center)
    worksheet.merge_range(35,8,39,12,'Percentage of targets, separated by personnel and starting position, out of all redzone passing plays in that personnel group.',center)
    worksheet.merge_range(12,8,17,12,"Personnel Group Definitions:\n(*) - 1 extra lineman\n(**) - 2 extra lineman\n(+Q) - extra QB\n(-Q) - no QB\n(D) - Defensive Player In\nUnknown - PFF couldn't decipher the personnel",center)

def summary():
    # PERSONNEL PERCENTAGE
    sorted = data.groupby(['pff_OFFPERSONNELBASIC']).size()/len(data)
    print(sorted)
    sorted.to_excel(writer, sheet_name='Summary',startrow = 15,startcol = 9+(count*3))
    worksheet = writer.sheets['Summary']
    worksheet.set_column(10+(count*3),10+(count*3), 12, format)
    colorhead('FLSO','TXUN',15,9,2,worksheet,sorted,.5,.65,'Personnel','Percentage')
    if (count == 1):
        worksheet.activate()

        # title
        worksheet.merge_range(5,8,13,14, "", largecenter)
        worksheet.write_rich_string(5,8,'Syracuse Off. Coordinator Breakdown\n',texas,'Texas (2016)\n',usf, 'USF (2017-18)',largecenter)

        # personnel breakdown
        worksheet.merge_range(0,0,40,6, "", writing)




    

while (not finish):
    FieldBdry(count)
    targeted(count)
    runbreakdown(count)
    earlydowns(count)
    thirddown(count)
    redzone(count)
    rbalignment()
    tealignment()
    summary()
    more = input("Are there more teams? ")
    if (more == 'Y'):
        count+=1
        team = input("Enter scouting team: ")
        data = pd.read_csv(r'/Users/HerschelGupta/Documents/FootballAnalytics/RawData/' + team + '_base_Cuse.csv')
        data['pff_RUNPASS'] = data['pff_RUNPASS'].replace(['R','P'],['Run','Pass'])
    else:
        finish = True
        descriptions()

writer.save()

from xlrd import open_workbook
wb = open_workbook('Module(2015SP).xlsx')
first_sheet = wb.sheet_by_index(0)
studentenroll = []
for a1 in range(0,10279):
    SE = []
    for a2 in range(0,18686):
        if first_sheet.cell_value(a2,0) > a1+1:
            break
        if first_sheet.cell_value(a2,0) == a1:
            SE.append(first_sheet.cell_value(a2,1))
    if len(SE)>1:
        studentenroll.append(SE)

import xlwt
wb2 = xlwt.Workbook()
ws = wb2.add_sheet('Sheet 1')

for i in range(1,127):
    for j in range(1,127):
        overlap = 0
        if i != j:
            for s in range(len(studentenroll)):
                if i in studentenroll[s] and j in studentenroll[s]:
                    overlap = overlap + 1
        ws.write(i,j,overlap)
        
wb2.save('overlapSpring.xls')
